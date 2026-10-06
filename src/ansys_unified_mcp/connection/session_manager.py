"""統一連線門面（AnsSessionManager）。

對應 Phase 3 任務 3.1（docs/reviews/2026-10-02-phase2-3-feasibility-assessment.md）。

**定位澄清**：此類別是對外呼叫介面的統一入口，不取代 `core/sessions.py` 的
`SessionRegistry`。所有實際連線邏輯仍由各產品既有的 `products/<name>/facade.py`
controller 負責，本類別僅依 `product` 參數委派給對應 controller 的 `connect`/`launch`
方法，不重新實作任何連線細節。

**為何不是單一簽名 `connect(product, port)`**：四個產品的 controller 參數並不一致——
`MechanicalController.connect(port, pid)` 用 `port`/`pid` 擇一定位目標；
`GeometryController.launch(port, host, transport_mode, connect_timeout)` 與
`FluentController.launch(processors, cwd, port, ip, password, connect_timeout)` 皆以
`launch` 身兼連線新舊實例兩種用途；`OptislangController.connect(project_path,
ini_timeout)` 完全沒有 port 概念（原生進程 API，非 gRPC）。勉強收斂成單一位置參數簽名
只會迫使呼叫端用 `None` 填補不適用的參數，反而降低可讀性。因此本類別以 `**kwargs`
透傳至對應 controller 的原生方法，呼叫端仍可使用該產品原本的參數名稱。
"""

from __future__ import annotations

from typing import Any, Literal

Product = Literal["mechanical", "geometry", "fluent", "optislang"]

_SUPPORTED_PRODUCTS = ("mechanical", "geometry", "fluent", "optislang")


class AnsSessionManager:
    """依 `product` 參數委派至對應產品 controller 的統一連線門面。"""

    @staticmethod
    def _unsupported_product_error(product: str) -> dict:
        return {
            "ok": False,
            "error": f"不支援的產品：{product!r}。支援的產品：{', '.join(_SUPPORTED_PRODUCTS)}。",
        }

    def connect(self, product: str, **kwargs: Any) -> dict:
        """連線至既有的 ANSYS 實例。

        各產品實際接受的參數不同，直接透傳至對應 controller：
        - mechanical: port, pid
        - geometry / fluent: 無獨立 connect，統一委派至 launch()（兩者的 launch 本身
          兼具「連線既有實例」與「啟動新實例」兩種行為，依是否傳入 port 判斷）
        - optislang: project_path, ini_timeout
        """
        if product == "mechanical":
            from ansys_unified_mcp.products.mechanical.facade import controller
            return controller.connect(**kwargs)
        if product == "geometry":
            from ansys_unified_mcp.products.geometry.facade import controller
            return controller.launch(**kwargs)
        if product == "fluent":
            from ansys_unified_mcp.products.fluent.facade import controller
            return controller.launch(**kwargs)
        if product == "optislang":
            from ansys_unified_mcp.products.optislang.facade import controller
            return controller.connect(**kwargs)
        return self._unsupported_product_error(product)

    def launch(self, product: str, **kwargs: Any) -> dict:
        """啟動新的 ANSYS 實例（或對無獨立 launch 概念的產品委派至其對應入口）。

        - mechanical: launch(batch)
        - geometry / fluent: launch(...)（同 connect，見上方說明）
        - optislang: 無獨立 launch，委派至 connect(project_path, ini_timeout)
          （optiSLang 的 Optislang() 建構子本身即身兼啟動進程與連線兩種行為）
        """
        if product == "mechanical":
            from ansys_unified_mcp.products.mechanical.facade import controller
            return controller.launch(**kwargs)
        if product == "geometry":
            from ansys_unified_mcp.products.geometry.facade import controller
            return controller.launch(**kwargs)
        if product == "fluent":
            from ansys_unified_mcp.products.fluent.facade import controller
            return controller.launch(**kwargs)
        if product == "optislang":
            from ansys_unified_mcp.products.optislang.facade import controller
            return controller.connect(**kwargs)
        return self._unsupported_product_error(product)

    def status(self, product: str, **kwargs: Any) -> dict:
        """查詢指定產品目前的連線狀態，委派至對應 controller 的 status()。"""
        if product == "mechanical":
            from ansys_unified_mcp.products.mechanical.facade import controller
            return controller.status()
        if product == "geometry":
            from ansys_unified_mcp.products.geometry.facade import controller
            return controller.status(**kwargs)
        if product == "fluent":
            from ansys_unified_mcp.products.fluent.facade import controller
            return controller.status(**kwargs)
        if product == "optislang":
            from ansys_unified_mcp.products.optislang.facade import controller
            return controller.status()
        return self._unsupported_product_error(product)

    def disconnect(self, product: str, **kwargs: Any) -> dict:
        """中斷指定產品的連線，委派至對應 controller 的 disconnect/exit/close。"""
        if product == "mechanical":
            from ansys_unified_mcp.products.mechanical.facade import controller
            return controller.disconnect(**kwargs)
        if product == "geometry":
            from ansys_unified_mcp.products.geometry.facade import controller
            return controller.close(**kwargs)
        if product == "fluent":
            from ansys_unified_mcp.products.fluent.facade import controller
            return controller.exit(**kwargs)
        if product == "optislang":
            from ansys_unified_mcp.products.optislang.facade import controller
            return controller.disconnect(**kwargs)
        return self._unsupported_product_error(product)


session_manager = AnsSessionManager()
