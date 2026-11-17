"""storage-lock HTTP 锁客户端。

薄网络客户端：只做 HTTP 调用，不重复实现 CAS 语义。服务端（storage-lock-http-api）
负责把锁的租约、fencing token 语义暴露成无状态接口。客户端拿到 owner_id 后必须
在租约内周期调用 renew 续租，否则锁会过期被他人抢占。
"""

import json
import urllib.error
import urllib.request


class LockBusyError(Exception):
    """锁被其他 owner 持有，本次获取失败（HTTP 409）。"""


class LockClient:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")

    def acquire(self, lock_id: str, owner_id: str = "", mode: str = "write",
                ttl: str = "", wait: bool = False) -> dict:
        """获取锁。成功返回 {owner_id, fencing_token, lease_expire}；被占用抛 LockBusyError。"""
        body = {"owner_id": owner_id, "mode": mode, "ttl": ttl, "wait": wait}
        return self._request("POST", f"/locks/{lock_id}/acquire", body)

    def renew(self, lock_id: str, owner_id: str) -> dict:
        """续租，延长租约。返回新的 {owner_id, lease_expire}。"""
        return self._request("POST", f"/locks/{lock_id}/renew", {"owner_id": owner_id})

    def release(self, lock_id: str, owner_id: str) -> dict:
        """释放锁。非 owner 释放会抛错。"""
        return self._request("POST", f"/locks/{lock_id}/release", {"owner_id": owner_id})

    def inspect(self, lock_id: str) -> dict:
        """查看锁的持有者、租约、等待队列。"""
        return self._request("GET", f"/locks/{lock_id}")

    def waiters(self, lock_id: str) -> list:
        return self._request("GET", f"/locks/{lock_id}/waiters")

    def list_locks(self) -> list:
        return self._request("GET", "/locks")

    def _request(self, method: str, path: str, body: dict | None = None) -> any:
        url = self.base_url + path
        data = None
        headers = {}
        if body is not None:
            data = json.dumps(body).encode()
            headers["Content-Type"] = "application/json"
        request = urllib.request.Request(url, data=data, headers=headers, method=method)
        try:
            with urllib.request.urlopen(request) as response:
                raw = response.read().decode()
                return json.loads(raw) if raw else None
        except urllib.error.HTTPError as e:
            if e.code == 409:
                raise LockBusyError(e.read().decode()) from e
            raise
