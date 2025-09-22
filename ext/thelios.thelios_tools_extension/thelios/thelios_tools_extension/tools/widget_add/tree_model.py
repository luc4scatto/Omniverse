import omni.ext
import omni.ui as ui

class SkuReleaseTreeModel(ui.AbstractItemModel):
    def __init__(self, query_results):
        super().__init__()
        self._columns = ["SKU", "RELEASE"]
        
        # Transform query results into hierarchical data structure
        self._data = self._organize_data(query_results)
    
    def _organize_data(self, results):
        # Assuming results is ['MODEL_ID', ('SKU1', 'RELEASE1'), ('SKU2', 'RELEASE2'), ...]
        if not results or len(results) < 2:
            return []
            
        model_id = results[0]  # First element is the MODEL
        skus = results[1:]     # Rest are tuples of (SKU, RELEASE)
        
        # Create a parent node for the MODEL
        model_node = {
            "name": model_id,  # Node name is the MODEL (used for header)
            "sku": None,       # MODEL has no SKU (None indicates parent node)
            "release": None,   # MODEL has no RELEASE
            "children": []
        }
        
        # Add SKUs as children
        for sku_data in skus:
            if isinstance(sku_data, tuple) and len(sku_data) == 2:
                sku, release = sku_data
                sku_node = {
                    "name": "",      # Empty name for child nodes
                    "sku": sku,      # Actual SKU
                    "release": release,
                    "children": []   # SKUs have no further children
                }
                model_node["children"].append(sku_node)
        
        return [model_node]  # Return a list with one element (MODEL node)

    def get_children(self, item):
        if item is None:
            # Return top-level nodes (MODELS)
            return self._data
        else:
            # Return children of the item (SKUs for MODELS)
            return item.get("children", [])

    def get_column_count(self):
        return len(self._columns)

    def get_item_value(self, item, column_id):
        # If it's a MODEL node (identified by sku=None), show it only in first column
        if item["sku"] is None and column_id == 0:
            return item["name"]
        
        # For SKU nodes, show values in appropriate columns
        if column_id == 0 and item["sku"] is not None:
            return item["sku"]
        elif column_id == 1 and item["release"] is not None:
            return item["release"]
            
        return ""  # Empty value for inapplicable columns

    def get_column_name(self, column_id):
        return self._columns[column_id]
        
    # Add the missing override method
    def get_item_value_model_count(self, item):
        # Return 0 since we're not using complex value models
        return 0
    
"""
class MyExtension(omni.ext.IExt):
    def on_startup(self, ext_id: str):
        print("TreeView Extension Starting")

        # Example query results
        query_results = ['DM40177I', ('01B', '261'), ('52N', '261'), ('57E', '261')]

        # Create model
        model = SkuReleaseTreeModel(query_results)

        # Build UI
        self._window = ui.Window("Query Results - TreeView", width=400, height=300)
        with self._window.frame:
            with ui.VStack():
                ui.Label("Model: " + query_results[0])  # Show model as label
                
                # Create TreeView with headers manually
                with ui.HStack(height=20):  # Header row
                    ui.Label("SKU", width=ui.Fraction(1/2))
                    ui.Label("RELEASE", width=ui.Fraction(1/2))
                
                # Create the TreeView
                self.tree_view = ui.TreeView(model)
                
                # Apply correct spacing for columns (UI-only, doesn't affect the model)
                self.tree_view.set_column_width(0, ui.Fraction(1/2))
                self.tree_view.set_column_width(1, ui.Fraction(1/2))

    def on_shutdown(self):
        print("TreeView Extension Terminated")
        self._window = None
"""