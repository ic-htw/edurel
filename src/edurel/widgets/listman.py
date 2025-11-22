import json
import os
from pathlib import Path
from typing import List, Optional
import ipywidgets as widgets
from IPython.display import display, Javascript
import base64


class ListManager:
    """
    Modular, reusable interactive list manager for Jupyter notebooks.
    Automatically saves/loads from JSON with filtering, sorting, and selection.
    """
    
    def __init__(self, filename: str = "list_data.json", directory: str = "."):
        self.filename = filename
        self.directory = Path(directory)
        self.directory.mkdir(parents=True, exist_ok=True)
        self.filepath = self.directory / filename
        
        self.items = []
        self.filtered_items = []
        self.selected_indices = set()
        self.sort_mode = "original"  # original, asc, desc
        
        self._load_data()
        self._create_widgets()
        self._setup_layout()
        self._update_display()
    
    def _load_data(self):
        """Load items from JSON file if it exists."""
        if self.filepath.exists():
            try:
                with open(self.filepath, 'r', encoding='utf-8') as f:
                    self.items = json.load(f)
            except Exception as e:
                print(f"Error loading file: {e}")
                self.items = []
        else:
            self.items = []
        self.filtered_items = self.items.copy()
    
    def _save_data(self):
        """Save items to JSON file."""
        try:
            with open(self.filepath, 'w', encoding='utf-8') as f:
                json.dump(self.items, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving file: {e}")
    
    def _create_widgets(self):
        """Create all UI widgets."""
        # Input section
        self.input_field = widgets.Text(
            placeholder='Enter item...',
            layout=widgets.Layout(width='70%')
        )
        self.add_btn = widgets.Button(
            description='Add',
            button_style='success',
            layout=widgets.Layout(width='25%')
        )
        
        # Search/Filter section
        self.search_field = widgets.Text(
            placeholder='Search/filter items...',
            layout=widgets.Layout(width='70%')
        )
        self.clear_filter_btn = widgets.Button(
            description='Clear Filter',
            button_style='info',
            layout=widgets.Layout(width='25%')
        )
        
        # Sorting buttons
        self.sort_asc_btn = widgets.Button(
            description='Sort A→Z',
            button_style='',
            layout=widgets.Layout(width='30%')
        )
        self.sort_desc_btn = widgets.Button(
            description='Sort Z→A',
            button_style='',
            layout=widgets.Layout(width='30%')
        )
        self.sort_original_btn = widgets.Button(
            description='Original Order',
            button_style='primary',
            layout=widgets.Layout(width='35%')
        )
        
        # File operations
        self.merge_checkbox = widgets.Checkbox(
            value=False,
            description='Merge on upload',
            layout=widgets.Layout(width='40%')
        )
        self.upload_btn = widgets.FileUpload(
            accept='.json',
            multiple=False,
            description='Upload JSON',
            layout=widgets.Layout(width='28%')
        )
        self.download_btn = widgets.Button(
            description='Download JSON',
            button_style='warning',
            layout=widgets.Layout(width='28%')
        )
        
        # Display area
        self.output_area = widgets.VBox(layout=widgets.Layout(
            width='100%',
            min_height='200px',
            border='1px solid #ddd',
            padding='10px',
            background='#f9f9f9',
            border_radius='5px'
        ))
        
        # Confirmation dialog (hidden by default)
        self.confirm_dialog = widgets.VBox(layout=widgets.Layout(display='none'))
        
        # Event handlers
        self.add_btn.on_click(self._on_add)
        self.input_field.on_submit(self._on_add)
        self.search_field.observe(self._on_search, names='value')
        self.clear_filter_btn.on_click(self._on_clear_filter)
        self.sort_asc_btn.on_click(lambda b: self._on_sort('asc'))
        self.sort_desc_btn.on_click(lambda b: self._on_sort('desc'))
        self.sort_original_btn.on_click(lambda b: self._on_sort('original'))
        self.upload_btn.observe(self._on_upload, names='value')
        self.download_btn.on_click(self._on_download)
    
    def _setup_layout(self):
        """Organize widgets into layout."""
        input_box = widgets.HBox(
            [self.input_field, self.add_btn],
            layout=widgets.Layout(width='100%', margin='5px 0')
        )
        
        search_box = widgets.HBox(
            [self.search_field, self.clear_filter_btn],
            layout=widgets.Layout(width='100%', margin='5px 0')
        )
        
        sort_box = widgets.HBox(
            [self.sort_asc_btn, self.sort_desc_btn, self.sort_original_btn],
            layout=widgets.Layout(width='100%', margin='5px 0')
        )
        
        file_box = widgets.HBox(
            [self.merge_checkbox, self.upload_btn, self.download_btn],
            layout=widgets.Layout(width='100%', margin='5px 0')
        )
        
        self.main_container = widgets.VBox([
            widgets.HTML('<h3 style="margin:5px 0;">List Manager</h3>'),
            input_box,
            search_box,
            sort_box,
            file_box,
            self.output_area,
            self.confirm_dialog
        ], layout=widgets.Layout(
            width='100%',
            padding='15px',
            background='#ffffff',
            border='2px solid #ddd',
            border_radius='8px'
        ))
    
    def _on_add(self, b):
        """Add new item to list."""
        text = self.input_field.value.strip()
        if text:
            self.items.append(text)
            self.input_field.value = ''
            self._save_data()
            self._apply_filter_and_sort()
            self._update_display()
    
    def _on_search(self, change):
        """Filter items based on search text."""
        self._apply_filter_and_sort()
        self._update_display()
    
    def _on_clear_filter(self, b):
        """Clear search filter."""
        self.search_field.value = ''
    
    def _on_sort(self, mode):
        """Change sort mode."""
        self.sort_mode = mode
        self._update_sort_buttons()
        self._apply_filter_and_sort()
        self._update_display()
    
    def _update_sort_buttons(self):
        """Update button styles based on active sort."""
        self.sort_asc_btn.button_style = 'primary' if self.sort_mode == 'asc' else ''
        self.sort_desc_btn.button_style = 'primary' if self.sort_mode == 'desc' else ''
        self.sort_original_btn.button_style = 'primary' if self.sort_mode == 'original' else ''
    
    def _apply_filter_and_sort(self):
        """Apply search filter and sorting to items."""
        search_text = self.search_field.value.lower()
        
        # Filter
        if search_text:
            self.filtered_items = [
                item for item in self.items 
                if search_text in item.lower()
            ]
        else:
            self.filtered_items = self.items.copy()
        
        # Sort
        if self.sort_mode == 'asc':
            self.filtered_items.sort(key=str.lower)
        elif self.sort_mode == 'desc':
            self.filtered_items.sort(key=str.lower, reverse=True)
        # 'original' keeps the current order
    
    def _update_display(self):
        """Refresh the display with current filtered items."""
        if not self.filtered_items:
            self.output_area.children = [
                widgets.HTML('<p style="color:#999;">No items to display</p>')
            ]
            return
        
        items_widgets = []
        for item in self.filtered_items:
            original_idx = self.items.index(item)
            
            checkbox = widgets.Checkbox(
                value=original_idx in self.selected_indices,
                indent=False,
                layout=widgets.Layout(width='30px', margin='0 5px 0 0')
            )
            checkbox.observe(
                lambda change, idx=original_idx: self._on_checkbox_change(change, idx),
                names='value'
            )
            
            label = widgets.Label(
                value=item,
                layout=widgets.Layout(flex='1', margin='0 10px')
            )
            
            edit_btn = widgets.Button(
                description='Edit',
                button_style='info',
                layout=widgets.Layout(width='80px')
            )
            edit_btn.on_click(lambda b, idx=original_idx: self._on_edit(idx))
            
            delete_btn = widgets.Button(
                description='Delete',
                button_style='danger',
                layout=widgets.Layout(width='80px')
            )
            delete_btn.on_click(lambda b, idx=original_idx: self._on_delete_confirm(idx))
            
            row = widgets.HBox(
                [checkbox, label, edit_btn, delete_btn],
                layout=widgets.Layout(
                    width='100%',
                    margin='3px 0',
                    padding='5px',
                    background='#ffffff',
                    border='1px solid #eee',
                    border_radius='3px'
                )
            )
            items_widgets.append(row)
        
        self.output_area.children = items_widgets
    
    def _on_checkbox_change(self, change, idx):
        """Handle checkbox selection."""
        if change['new']:
            self.selected_indices.add(idx)
        else:
            self.selected_indices.discard(idx)
    
    def _on_edit(self, idx):
        """Edit an item."""
        old_value = self.items[idx]
        new_value_widget = widgets.Text(value=old_value, layout=widgets.Layout(width='70%'))
        
        def save_edit(b):
            new_val = new_value_widget.value.strip()
            if new_val:
                self.items[idx] = new_val
                # Update selected indices if item was selected
                if idx in self.selected_indices:
                    self.selected_indices.add(idx)
                self._save_data()
                self._apply_filter_and_sort()
                self._update_display()
                self.confirm_dialog.layout.display = 'none'
        
        def cancel_edit(b):
            self.confirm_dialog.layout.display = 'none'
            self._update_display()
        
        save_btn = widgets.Button(description='Save', button_style='success')
        cancel_btn = widgets.Button(description='Cancel', button_style='')
        save_btn.on_click(save_edit)
        cancel_btn.on_click(cancel_edit)
        
        self.confirm_dialog.children = [
            widgets.HTML('<h4>Edit Item</h4>'),
            new_value_widget,
            widgets.HBox([save_btn, cancel_btn])
        ]
        self.confirm_dialog.layout.display = 'block'
    
    def _on_delete_confirm(self, idx):
        """Show delete confirmation dialog."""
        item_text = self.items[idx]
        
        def confirm_delete(b):
            self.items.pop(idx)
            # Update selected indices
            self.selected_indices.discard(idx)
            new_selected = set()
            for si in self.selected_indices:
                if si > idx:
                    new_selected.add(si - 1)
                else:
                    new_selected.add(si)
            self.selected_indices = new_selected
            
            self._save_data()
            self._apply_filter_and_sort()
            self._update_display()
            self.confirm_dialog.layout.display = 'none'
        
        def cancel_delete(b):
            self.confirm_dialog.layout.display = 'none'
        
        yes_btn = widgets.Button(description='Yes, Delete', button_style='danger')
        cancel_btn = widgets.Button(description='Cancel', button_style='')
        yes_btn.on_click(confirm_delete)
        cancel_btn.on_click(cancel_delete)
        
        self.confirm_dialog.children = [
            widgets.HTML(f'<h4>Delete Item?</h4><p>{item_text}</p>'),
            widgets.HBox([yes_btn, cancel_btn])
        ]
        self.confirm_dialog.layout.display = 'block'
    
    def _on_upload(self, change):
        """Handle JSON file upload."""
        if not self.upload_btn.value:
            return
        
        uploaded_file = list(self.upload_btn.value.values())[0]
        try:
            content = uploaded_file['content']
            json_str = content.decode('utf-8')
            new_items = json.loads(json_str)
            
            if not isinstance(new_items, list):
                print("Error: JSON must contain a list")
                return
            
            if self.merge_checkbox.value:
                # Merge: add only new items
                existing_set = set(self.items)
                for item in new_items:
                    if item not in existing_set:
                        self.items.append(item)
            else:
                # Replace
                self.items = new_items
                self.selected_indices.clear()
            
            self._save_data()
            self._apply_filter_and_sort()
            self._update_display()
            print(f"✓ Uploaded successfully ({'merged' if self.merge_checkbox.value else 'replaced'})")
        except Exception as e:
            print(f"Error uploading file: {e}")
        finally:
            self.upload_btn.value = ()
    
    def _on_download(self, b):
        """Download current list as JSON."""
        json_str = json.dumps(self.items, indent=2, ensure_ascii=False)
        b64 = base64.b64encode(json_str.encode()).decode()
        
        js_code = f"""
        var link = document.createElement('a');
        link.href = 'data:application/json;base64,{b64}';
        link.download = '{self.filename}';
        link.click();
        """
        display(Javascript(js_code))
    
    def get_selected_items(self) -> List[str]:
        """Return list of selected items."""
        return [self.items[idx] for idx in sorted(self.selected_indices) if idx < len(self.items)]
    
    def display(self):
        """Display the list manager widget."""
        display(self.main_container)


# Example usage:
# manager = ListManager(filename="my_list.json", directory="./data")
# manager.display()
# 
# # Get selected items:
# selected = manager.get_selected_items()
# print(selected)