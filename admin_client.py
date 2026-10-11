"""只读管理客户端。查询持有者、剩余租约和等待队列，不提供强制解锁。"""

import urllib.request


class AdminClient:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")

    def list_locks(self) -> str:
        return self._get("/locks")

    def get_lock(self, lock_id: str) -> str:
        return self._get(f"/locks/{lock_id}")

    def waiters(self, lock_id: str) -> str:
        return self._get(f"/locks/{lock_id}/waiters")

    def _get(self, path: str) -> str:
        with urllib.request.urlopen(self.base_url + path) as response:
            return response.read().decode()
