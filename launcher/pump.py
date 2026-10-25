"""pump.fun via PumpPortal's Local Transaction API: transactions are built remotely, signed only on this machine.

Single wallet by design. There is deliberately no standalone buy: the only buy this bot ever makes is the
dev buy inside the create transaction.
"""
import json
import time

import requests
from solders.commitment_config import CommitmentLevel
from solders.keypair import Keypair
from solders.rpc.config import RpcSendTransactionConfig
from solders.rpc.requests import SendVersionedTransaction
from solders.transaction import VersionedTransaction

PINATA_URL = "https://uploads.pinata.cloud/v3/files"
TRADE_LOCAL = "https://pumpportal.fun/api/trade-local"


class Pump:
    def __init__(self, keypair: Keypair, rpc_url: str, pinata_jwt: str):
        self.kp = keypair
        self.pubkey = str(keypair.pubkey())
        self.rpc = rpc_url
        self.pinata_jwt = pinata_jwt

    # ---------- metadata
    def _pin(self, filename: str, data: bytes, mime: str) -> str:
        r = requests.post(PINATA_URL, headers={"Authorization": f"Bearer {self.pinata_jwt}"},
                          data={"network": "public"}, files={"file": (filename, data, mime)}, timeout=30)
        r.raise_for_status()
        return r.json()["data"]["cid"]

    def upload_metadata(self, name: str, ticker: str, description: str, image: bytes, mime: str,
                        tweet_url: str) -> str:
        image_cid = self._pin(f"{ticker}.png", image, mime)
        meta = {"name": name, "symbol": ticker, "description": description,
                "image": f"https://ipfs.io/ipfs/{image_cid}", "showName": True,
                "twitter": tweet_url, "telegram": "", "website": ""}
        meta_cid = self._pin(f"{ticker}.json", json.dumps(meta).encode(), "application/json")
        return f"https://ipfs.io/ipfs/{meta_cid}"

    # ---------- transactions
    def _build(self, payload: dict, signers: list) -> VersionedTransaction:
        r = requests.post(TRADE_LOCAL, json=payload, timeout=20)
        if r.status_code != 200:
            raise RuntimeError(f"PumpPortal {r.status_code}: {r.text[:200]}")
        unsigned = VersionedTransaction.from_bytes(r.content)
        return VersionedTransaction(unsigned.message, signers)

    def _send(self, tx: VersionedTransaction) -> str:
        cfg = RpcSendTransactionConfig(preflight_commitment=CommitmentLevel.Confirmed)
        r = requests.post(self.rpc, headers={"Content-Type": "application/json"},
                          data=SendVersionedTransaction(tx, cfg).to_json(), timeout=20)
        body = r.json()
        if "error" in body:
            raise RuntimeError(f"RPC send failed: {body['error']}")
        return body["result"]

    def confirm(self, sig: str, timeout: float = 60) -> bool:
        end = time.time() + timeout
        while time.time() < end:
            body = requests.post(self.rpc, json={"jsonrpc": "2.0", "id": 1, "method": "getSignatureStatuses",
                                                 "params": [[sig], {"searchTransactionHistory": False}]},
                                 timeout=10).json()
            status = (body.get("result") or {}).get("value", [None])[0]
            if status:
                if status.get("err"):
                    return False
                if status.get("confirmationStatus") in ("confirmed", "finalized"):
                    return True
            time.sleep(1.5)
        return False

    def create(self, mint: Keypair, name: str, ticker: str, uri: str, dev_buy_sol: float,
               slippage: float, priority_fee: float) -> str:
        payload = {"publicKey": self.pubkey, "action": "create",
                   "tokenMetadata": {"name": name, "symbol": ticker, "uri": uri},
                   "mint": str(mint.pubkey()), "denominatedInSol": "true", "amount": dev_buy_sol,
                   "slippage": slippage, "priorityFee": priority_fee, "pool": "pump"}
        return self._send(self._build(payload, [mint, self.kp]))

    def sell_all(self, mint: str, slippage: float, priority_fee: float) -> str:
        payload = {"publicKey": self.pubkey, "action": "sell", "mint": mint, "amount": "100%",
                   "denominatedInSol": "false", "slippage": slippage, "priorityFee": priority_fee,
                   "pool": "auto"}
        return self._send(self._build(payload, [self.kp]))

    def claim_creator_fees(self, priority_fee: float) -> str:
        payload = {"publicKey": self.pubkey, "action": "collectCreatorFee", "priorityFee": priority_fee}
        return self._send(self._build(payload, [self.kp]))

    def balance_sol(self) -> float:
        body = requests.post(self.rpc, json={"jsonrpc": "2.0", "id": 1, "method": "getBalance",
                                             "params": [self.pubkey]}, timeout=10).json()
        return body["result"]["value"] / 1e9
