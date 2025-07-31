"""
EPLua GUI Module with Native tkinter Rendering

This module provides GUI capabilities usi            self.window.geometry(f"{self.width}x{self.height}")
            
            # Hide window initially
            self.window.withdraw()
            self.created = True
            
            global window_registry widgets.
Windows can be created, controlled, and closed from Lua scripts.
Dynamic UI building from JSON descriptions is supported.
"""

import logging
import threading
import uuid
from typing import Dict, Optional, Any
import tkinter as tk
from tkinter import ttk

# Set up logging
logger = logging.getLogger(__name__)

# Global state
window_registry: Dict[str, 'UIWindow'] = {}
main_app = None
gui_thread = None

try:
    import tkinter as tk
    from tkinter import ttk, messagebox
    TKINTER_AVAILABLE = True
    GUI_AVAILABLE = True
    logger.info("tkinter is available")
except ImportError:
    TKINTER_AVAILABLE = False
    GUI_AVAILABLE = False
    logger.warning("tkinter is not available")

# Import HTML label support
try:
    from .html_label import SimpleHTMLLabel, create_html_label
    HTML_RENDERING_AVAILABLE = True
    HTML_ENGINE = "simple"
    logger.info("Simple HTML rendering is available")
except ImportError:
    HTML_RENDERING_AVAILABLE = False
    HTML_ENGINE = "none"
    logger.warning("HTML label support not available")

import json
import logging
import tkinter as tk
from tkinter import ttk
import uuid
from typing import Dict, List, Any, Optional, Callable

logger = logging.getLogger(__name__)

# Global registry for tracking windows
window_registry = {}

# Global reference to the main tkinter root (set by CLI)
_main_tkinter_root = None

def set_main_tkinter_root(root):
    """Set the main tkinter root for cleanup coordination"""
    global _main_tkinter_root
    _main_tkinter_root = root

def signal_main_loop_quit():
    """Signal the main tkinter loop to quit"""
    global _main_tkinter_root
    if _main_tkinter_root:
        try:
            _main_tkinter_root.quit()
        except:
            pass


class UIWindow:
    """A native tkinter window with dynamic UI building capabilities"""
    
    def __init__(self, window_id: str, title: str, width: int = 800, height: int = 600):
        self.window_id = window_id
        self.title = title
        self.width = width
        self.height = height
        self.window = None
        self.created = False
        self.widgets = {}
        self.callbacks = {}
        self.ui_description = None
        
    def create(self):
        """Create the tkinter window"""
        if self.created:
            return
            
        try:
            # Create the window using macOS-friendly approach
            global main_app
            if main_app is None:
                # First window becomes the main application window
                self.window = tk.Tk()
                main_app = self.window
                logger.info(f"Created main Tk() window for {self.window_id}")
                
                # On macOS, ensure proper app termination behavior
                try:
                    # Set the window to quit the entire application when closed
                    self.window.protocol("WM_DELETE_WINDOW", self._on_main_window_close)
                    
                    # Try to set macOS-specific behavior
                    if hasattr(self.window, 'createcommand'):
                        # Register proper app termination
                        self.window.createcommand('exit', lambda: self._quit_application())
                except:
                    pass
            else:
                self.window = tk.Toplevel(main_app)
                logger.info(f"Created Toplevel() window for {self.window_id}")
                # Set up normal window close for secondary windows
                self.window.protocol("WM_DELETE_WINDOW", self._on_window_close)
            
            self.window.title(self.title)
            self.window.geometry(f"{self.width}x{self.height}")
            
            # Hide window initially
            self.window.withdraw()
            self.created = True
            
            global window_registry
            window_registry[self.window_id] = self
            logger.info(f"UI window {self.window_id} created successfully")
            
        except Exception as e:
            logger.error(f"Failed to create UI window {self.window_id}: {e}")
            raise
    
    def set_ui(self, ui_description: Dict[str, Any]):
        """Build UI from JSON description"""
        if not self.created:
            self.create()
        
        self.ui_description = ui_description
        
        try:
            # Clear existing widgets
            for widget in self.window.winfo_children():
                widget.destroy()
            self.widgets.clear()
            
            # Create main container with padding
            padding = ui_description.get('padding', 20)
            main_frame = ttk.Frame(self.window, padding=str(padding))
            main_frame.pack(fill=tk.BOTH, expand=True)
            
            # Handle hierarchical format (with 'children') or flat format (with 'elements')
            if 'children' in ui_description:
                # Hierarchical format
                self._build_hierarchical_ui(main_frame, ui_description)
            elif 'elements' in ui_description:
                # Flat format
                elements = ui_description.get('elements', [])
                for i, element in enumerate(elements):
                    self._create_element(main_frame, element, i)
                logger.info(f"UI built for window {self.window_id} with {len(elements)} elements")
            else:
                # Single element format
                if ui_description.get('type'):
                    self._create_hierarchical_element(main_frame, ui_description)
                    logger.info(f"UI built for window {self.window_id} with single element")
            
        except Exception as e:
            logger.error(f"Failed to build UI for window {self.window_id}: {e}")
            raise
    
    def _build_hierarchical_ui(self, parent: tk.Widget, ui_element: Dict[str, Any]):
        """Build UI from hierarchical description"""
        if ui_element.get('type') == 'frame' or not ui_element.get('type'):
            # This is a container, process its children
            children = ui_element.get('children', [])
            for child in children:
                self._create_hierarchical_element(parent, child)
            logger.info(f"UI built for window {self.window_id} with {len(children)} elements")
        else:
            # Single element
            self._create_hierarchical_element(parent, ui_element)
    
    def _create_hierarchical_element(self, parent: tk.Widget, element: Dict[str, Any]):
        """Create a UI element from hierarchical description"""
        element_type = element.get('type', '').lower()
        element_id = element.get('id', f'element_{len(self.widgets)}')
        
        # Handle different widget types
        if element_type == 'label':
            self._create_hierarchical_label(parent, element, element_id)
        elif element_type == 'button':
            self._create_hierarchical_button(parent, element, element_id)
        elif element_type == 'entry':
            self._create_hierarchical_entry(parent, element, element_id)
        elif element_type == 'text':
            self._create_hierarchical_text(parent, element, element_id)
        elif element_type == 'checkbox':
            self._create_hierarchical_checkbox(parent, element, element_id)
        elif element_type == 'radio':
            self._create_hierarchical_radio(parent, element, element_id)
        elif element_type == 'combobox':
            self._create_hierarchical_combobox(parent, element, element_id)
        elif element_type == 'listbox':
            self._create_hierarchical_listbox(parent, element, element_id)
        elif element_type == 'scale':
            self._create_hierarchical_scale(parent, element, element_id)
        elif element_type == 'progressbar':
            self._create_hierarchical_progressbar(parent, element, element_id)
        elif element_type == 'separator':
            self._create_hierarchical_separator(parent, element, element_id)
        elif element_type == 'frame':
            self._create_hierarchical_frame(parent, element, element_id)
        else:
            logger.warning(f"Unknown element type: {element_type}")
    
    def _create_hierarchical_label(self, parent: tk.Widget, element: Dict[str, Any], element_id: str):
        """Create a label widget"""
        text = element.get('text', 'Label')
        font = element.get('font', None)
        
        widget = ttk.Label(parent, text=text)
        if font and isinstance(font, list) and len(font) >= 2:
            try:
                widget.configure(font=(font[0], font[1]))
            except:
                pass
        
        # Handle layout
        sticky = element.get('sticky', '')
        if sticky:
            widget.pack(fill=tk.X if 'e' in sticky and 'w' in sticky else tk.NONE, 
                       expand='x' in sticky.lower(), pady=2)
        else:
            widget.pack(pady=2)
        
        self.widgets[element_id] = widget
    
    def _create_hierarchical_button(self, parent: tk.Widget, element: Dict[str, Any], element_id: str):
        """Create a button widget"""
        text = element.get('text', 'Button')
        callback_name = element.get('callback', '')
        
        def button_callback():
            if callback_name:
                self._handle_callback(element_id, callback_name, {'element_id': element_id, 'window_id': self.window_id})
        
        widget = ttk.Button(parent, text=text, command=button_callback)
        widget.pack(pady=2)
        
        self.widgets[element_id] = widget
    
    def _create_hierarchical_entry(self, parent: tk.Widget, element: Dict[str, Any], element_id: str):
        """Create an entry widget"""
        placeholder = element.get('placeholder', '')
        value = element.get('value', '')
        
        widget = ttk.Entry(parent)
        if value:
            widget.insert(0, value)
        elif placeholder:
            # Simple placeholder simulation
            widget.insert(0, placeholder)
            widget.config(foreground='gray')
            
            def on_focus_in(event):
                if widget.get() == placeholder:
                    widget.delete(0, tk.END)
                    widget.config(foreground='black')
            
            def on_focus_out(event):
                if not widget.get():
                    widget.insert(0, placeholder)
                    widget.config(foreground='gray')
            
            widget.bind('<FocusIn>', on_focus_in)
            widget.bind('<FocusOut>', on_focus_out)
        
        widget.pack(fill=tk.X, pady=2)
        self.widgets[element_id] = widget
    
    def _create_hierarchical_text(self, parent: tk.Widget, element: Dict[str, Any], element_id: str):
        """Create a text widget"""
        value = element.get('value', '')
        state = element.get('state', 'normal')
        
        # Create a frame for text widget with scrollbar
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.BOTH, expand=True, pady=2)
        
        widget = tk.Text(frame, height=6, state=state)
        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=widget.yview)
        widget.configure(yscrollcommand=scrollbar.set)
        
        widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        if value:
            widget.insert(tk.END, value)
        
        self.widgets[element_id] = widget
    
    def _create_hierarchical_checkbox(self, parent: tk.Widget, element: Dict[str, Any], element_id: str):
        """Create a checkbox widget"""
        text = element.get('text', 'Checkbox')
        value = element.get('value', False)
        
        var = tk.BooleanVar(value=value)
        widget = ttk.Checkbutton(parent, text=text, variable=var)
        widget.pack(anchor=tk.W, pady=2)
        
        self.widgets[element_id] = {'widget': widget, 'var': var}
    
    def _create_hierarchical_radio(self, parent: tk.Widget, element: Dict[str, Any], element_id: str):
        """Create a radio button widget"""
        text = element.get('text', 'Radio')
        value = element.get('value', '')
        group = element.get('group', 'default')
        
        # Get or create StringVar for this radio group
        if not hasattr(self, '_radio_groups'):
            self._radio_groups = {}
        if group not in self._radio_groups:
            self._radio_groups[group] = tk.StringVar()
        
        var = self._radio_groups[group]
        if element.get('selected', False):
            var.set(value)
        
        widget = ttk.Radiobutton(parent, text=text, variable=var, value=value)
        widget.pack(anchor=tk.W, pady=2)
        
        self.widgets[element_id] = {'widget': widget, 'var': var}
    
    def _create_hierarchical_combobox(self, parent: tk.Widget, element: Dict[str, Any], element_id: str):
        """Create a combobox widget"""
        options = element.get('options', ['Option 1', 'Option 2'])
        value = element.get('value', options[0] if options else '')
        
        var = tk.StringVar(value=value)
        widget = ttk.Combobox(parent, textvariable=var, values=options, state='readonly')
        widget.pack(fill=tk.X, pady=2)
        
        self.widgets[element_id] = {'widget': widget, 'var': var}
    
    def _create_hierarchical_listbox(self, parent: tk.Widget, element: Dict[str, Any], element_id: str):
        """Create a listbox widget"""
        options = element.get('options', ['Item 1', 'Item 2', 'Item 3'])
        
        # Create frame with scrollbar
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.BOTH, expand=True, pady=2)
        
        widget = tk.Listbox(frame)
        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=widget.yview)
        widget.configure(yscrollcommand=scrollbar.set)
        
        for option in options:
            widget.insert(tk.END, option)
        
        widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.widgets[element_id] = widget
    
    def _create_hierarchical_scale(self, parent: tk.Widget, element: Dict[str, Any], element_id: str):
        """Create a scale (slider) widget"""
        from_val = element.get('from', 0)
        to_val = element.get('to', 100)
        value = element.get('value', from_val)
        orient = element.get('orient', 'horizontal')
        
        def on_change(val):
            self._handle_callback(element_id, 'change', {'value': float(val), 'element_id': element_id, 'window_id': self.window_id})
        
        widget = ttk.Scale(parent, from_=from_val, to=to_val, value=value, 
                          orient=orient, command=on_change)
        widget.pack(fill=tk.X, pady=2)
        
        self.widgets[element_id] = widget
    
    def _create_hierarchical_progressbar(self, parent: tk.Widget, element: Dict[str, Any], element_id: str):
        """Create a progressbar widget"""
        value = element.get('value', 0)
        maximum = element.get('maximum', 100)
        orient = element.get('orient', 'horizontal')
        
        widget = ttk.Progressbar(parent, value=value, maximum=maximum, orient=orient)
        widget.pack(fill=tk.X, pady=2)
        
        self.widgets[element_id] = widget
    
    def _create_hierarchical_separator(self, parent: tk.Widget, element: Dict[str, Any], element_id: str):
        """Create a separator widget"""
        orient = element.get('orient', 'horizontal')
        
        widget = ttk.Separator(parent, orient=orient)
        widget.pack(fill=tk.X, pady=5)
        
        self.widgets[element_id] = widget
    
    def _create_hierarchical_frame(self, parent: tk.Widget, element: Dict[str, Any], element_id: str):
        """Create a frame widget with children"""
        padding = element.get('padding', 10)
        
        widget = ttk.Frame(parent, padding=str(padding))
        widget.pack(fill=tk.BOTH, expand=True, pady=2)
        
        # Process children
        children = element.get('children', [])
        for child in children:
            self._create_hierarchical_element(widget, child)
        
        self.widgets[element_id] = widget
    
    def _create_element(self, parent: tk.Widget, element: Dict[str, Any], row: int):
        """Create a single UI element"""
        element_type = element.get('type', '').lower()
        element_id = element.get('id', f'element_{row}')
        
        # Create row frame
        row_frame = ttk.Frame(parent)
        row_frame.pack(fill=tk.X, pady=5)
        
        if element_type == 'label':
            self._create_label(row_frame, element, element_id)
        elif element_type == 'button':
            self._create_button(row_frame, element, element_id)
        elif element_type == 'switch':
            self._create_switch(row_frame, element, element_id)
        elif element_type == 'slider':
            self._create_slider(row_frame, element, element_id)
        elif element_type == 'dropdown':
            self._create_dropdown(row_frame, element, element_id)
        elif element_type == 'multiselect':
            self._create_multiselect(row_frame, element, element_id)
        elif element_type == 'header':
            self._create_header(row_frame, element, element_id)
        elif element_type == 'separator':
            self._create_separator(row_frame, element, element_id)
        elif element_type == 'button_row':
            self._create_button_row(row_frame, element, element_id)
        else:
            logger.warning(f"Unknown element type: {element_type}")
    
    def _create_label(self, parent: tk.Widget, element: Dict[str, Any], element_id: str):
        """Create a label with optional HTML support"""
        text = element.get('text', 'Label')
        style = element.get('style', {})
        html = element.get('html', False)  # Check if HTML rendering is requested
        
        if html and HTML_RENDERING_AVAILABLE:
            # Use HTML label for rich text
            try:
                label = SimpleHTMLLabel(parent, text, height=1, width=30, 
                                      borderwidth=0, relief=tk.FLAT)
                label.pack(side=tk.LEFT, padx=(0, 10))
                self.widgets[element_id] = label.text_widget  # Store the actual text widget
            except Exception as e:
                logger.warning(f"HTML label creation failed, falling back to regular label: {e}")
                # Fall back to regular label
                label = ttk.Label(parent, text=text)
                label.pack(side=tk.LEFT, padx=(0, 10))
                self.widgets[element_id] = label
        else:
            # Regular label
            label = ttk.Label(parent, text=text)
            label.pack(side=tk.LEFT, padx=(0, 10))
            self.widgets[element_id] = label
    
    def _create_button(self, parent: tk.Widget, element: Dict[str, Any], element_id: str):
        """Create a button"""
        text = element.get('text', 'Button')
        action = element.get('action', '')
        style = element.get('style', {})
        
        def button_callback():
            self._handle_callback(element_id, 'click', {'action': action})
        
        # Check if it's a primary button
        button_style = 'Accent.TButton' if style.get('primary') else 'TButton'
        
        button = ttk.Button(parent, text=text, command=button_callback, style=button_style)
        button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.widgets[element_id] = button
    
    def _create_switch(self, parent: tk.Widget, element: Dict[str, Any], element_id: str):
        """Create a switch (checkbox)"""
        text = element.get('text', 'Switch')
        default_value = element.get('value', False)
        
        var = tk.BooleanVar(value=default_value)
        
        def switch_callback():
            self._handle_callback(element_id, 'change', {'value': var.get()})
        
        switch = ttk.Checkbutton(parent, text=text, variable=var, command=switch_callback)
        switch.pack(side=tk.LEFT, padx=(0, 10))
        
        self.widgets[element_id] = {'widget': switch, 'var': var}
    
    def _create_slider(self, parent: tk.Widget, element: Dict[str, Any], element_id: str):
        """Create a slider"""
        text = element.get('text', 'Slider')
        min_value = element.get('min', 0)
        max_value = element.get('max', 100)
        default_value = element.get('value', 50)
        
        # Create container for label and slider
        container = ttk.Frame(parent)
        container.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        # Label
        if text:
            label = ttk.Label(container, text=text)
            label.pack(side=tk.LEFT, padx=(0, 10))
        
        # Value display
        value_var = tk.StringVar(value=str(default_value))
        value_label = ttk.Label(container, textvariable=value_var, width=5)
        value_label.pack(side=tk.RIGHT, padx=(10, 0))
        
        # Slider
        def slider_callback(value):
            value_var.set(str(int(float(value))))
            self._handle_callback(element_id, 'change', {'value': int(float(value))})
        
        slider = ttk.Scale(container, from_=min_value, to=max_value, 
                          value=default_value, command=slider_callback)
        slider.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        self.widgets[element_id] = {'widget': slider, 'var': value_var}
    
    def _create_dropdown(self, parent: tk.Widget, element: Dict[str, Any], element_id: str):
        """Create a dropdown (combobox)"""
        text = element.get('text', 'Select')
        options = element.get('options', ['Option 1', 'Option 2'])
        default_value = element.get('value', options[0] if options else '')
        
        # Create container
        container = ttk.Frame(parent)
        container.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        # Label
        if text:
            label = ttk.Label(container, text=text)
            label.pack(side=tk.LEFT, padx=(0, 10))
        
        # Dropdown
        var = tk.StringVar(value=default_value)
        
        def dropdown_callback(event):
            # Get value directly from the combobox widget to avoid timing issues
            selected_value = dropdown.get()
            self._handle_callback(element_id, 'change', {'value': selected_value})
        
        dropdown = ttk.Combobox(container, textvariable=var, values=options, state='readonly')
        dropdown.pack(side=tk.LEFT, padx=(0, 10))
        dropdown.bind('<<ComboboxSelected>>', dropdown_callback)
        
        self.widgets[element_id] = {'widget': dropdown, 'var': var}
    
    def _create_multiselect(self, parent: tk.Widget, element: Dict[str, Any], element_id: str):
        """Create a multiselect listbox"""
        text = element.get('text', 'Multi-select')
        options = element.get('options', ['Option 1', 'Option 2', 'Option 3'])
        default_values = element.get('values', [])
        height = element.get('height', 4)
        
        # Create container
        container = ttk.Frame(parent)
        container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Label
        if text:
            label = ttk.Label(container, text=text)
            label.pack(side=tk.TOP, anchor=tk.W, pady=(0, 5))
        
        # Listbox with scrollbar
        listbox_frame = ttk.Frame(container)
        listbox_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        listbox = tk.Listbox(listbox_frame, selectmode=tk.MULTIPLE, height=height)
        scrollbar = ttk.Scrollbar(listbox_frame, orient=tk.VERTICAL, command=listbox.yview)
        listbox.configure(yscrollcommand=scrollbar.set)
        
        listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Populate options
        for option in options:
            listbox.insert(tk.END, option)
        
        # Set default selections
        for value in default_values:
            if value in options:
                listbox.selection_set(options.index(value))
        
        def multiselect_callback(event):
            selected_indices = listbox.curselection()
            selected_values = [options[i] for i in selected_indices]
            self._handle_callback(element_id, 'change', {'values': selected_values})
        
        listbox.bind('<<ListboxSelect>>', multiselect_callback)
        
        self.widgets[element_id] = {'widget': listbox, 'options': options}
    
    def _create_header(self, parent: tk.Widget, element: Dict[str, Any], element_id: str):
        """Create a header/title"""
        text = element.get('text', 'Header')
        level = element.get('level', 1)  # 1-3 for different sizes
        
        # Configure font based on level
        font_sizes = {1: ('TkDefaultFont', 16, 'bold'), 
                     2: ('TkDefaultFont', 14, 'bold'), 
                     3: ('TkDefaultFont', 12, 'bold')}
        font = font_sizes.get(level, font_sizes[1])
        
        header = tk.Label(parent, text=text, font=font, bg='#f0f0f0')
        header.pack(side=tk.LEFT, anchor=tk.W)
        
        self.widgets[element_id] = header
    
    def _create_separator(self, parent: tk.Widget, element: Dict[str, Any], element_id: str):
        """Create a separator line"""
        separator = ttk.Separator(parent, orient=tk.HORIZONTAL)
        separator.pack(side=tk.LEFT, fill=tk.X, expand=True, pady=10)
        
        self.widgets[element_id] = separator
    
    def _create_button_row(self, parent: tk.Widget, element: Dict[str, Any], element_id: str):
        """Create a horizontal row of buttons"""
        buttons = element.get('buttons', [])
        
        # Create a frame for the button row
        button_row_frame = ttk.Frame(parent)
        button_row_frame.pack(fill=tk.X, pady=5)
        
        # Create buttons horizontally
        for btn_info in buttons:
            text = btn_info.get('text', 'Button')
            action = btn_info.get('action', '')
            style = btn_info.get('style', {})
            btn_id = btn_info.get('id', f'btn_{len(self.widgets)}')
            
            def button_callback(btn_action=action, btn_id=btn_id):
                self._handle_callback(btn_id, 'click', {'action': btn_action})
            
            # Check if it's a primary button
            button_style = 'Accent.TButton' if style.get('primary') else 'TButton'
            
            button = ttk.Button(button_row_frame, text=text, command=button_callback, style=button_style)
            button.pack(side=tk.LEFT, padx=(0, 10), pady=2)
            
            # Store individual button references
            self.widgets[btn_id] = button
        
        # Store the frame reference as well
        self.widgets[element_id] = button_row_frame
    
    def _handle_callback(self, element_id: str, event_type: str, data: Dict[str, Any]):
        """Handle widget callbacks"""
        callback_data = {
            'window_id': self.window_id,
            'element_id': element_id,
            'event_type': event_type,
            'data': data
        }
        
        # Call registered callback if exists
        if element_id in self.callbacks:
            try:
                self.callbacks[element_id](callback_data)
            except Exception as e:
                logger.error(f"Callback error for {element_id}: {e}")
        
        # Also log for debugging
        logger.info(f"UI Event: {callback_data}")
    
    def set_callback(self, element_id: str, callback: Callable):
        """Set a callback for a specific element"""
        self.callbacks[element_id] = callback
    
    def get_value(self, element_id: str):
        """Get the current value of an element"""
        if element_id not in self.widgets:
            return None
        
        widget_info = self.widgets[element_id]
        
        if isinstance(widget_info, dict):
            if 'var' in widget_info:
                return widget_info['var'].get()
            elif 'widget' in widget_info and hasattr(widget_info['widget'], 'curselection'):
                # Multiselect
                selected_indices = widget_info['widget'].curselection()
                return [widget_info['options'][i] for i in selected_indices]
        
        return None
    
    def set_value(self, element_id: str, value: Any):
        """Set the value of an element"""
        if element_id not in self.widgets:
            return
        
        widget_info = self.widgets[element_id]
        
        # Handle widgets with variables (sliders, entries, etc.)
        if isinstance(widget_info, dict) and 'var' in widget_info:
            widget_info['var'].set(value)
        # Handle labels by updating their text directly
        elif hasattr(widget_info, 'configure'):
            try:
                widget_info.configure(text=str(value))
                logger.info(f"Updated label {element_id} text to: {value}")
            except Exception as e:
                logger.warning(f"Failed to update widget {element_id}: {e}")
        else:
            logger.warning(f"Cannot set value for widget {element_id}: unsupported widget type")
    
    def show(self):
        """Show the window"""
        if not self.created:
            self.create()
        
        if self.window:
            self.window.deiconify()
            self.window.lift()
            logger.info(f"UI window {self.window_id} shown")
    
    def hide(self):
        """Hide the window"""
        if self.window:
            self.window.withdraw()
            logger.info(f"UI window {self.window_id} hidden")

    def update_element(self, element_id: str, property_name: str, value: Any) -> bool:
        """Update a specific element property"""
        if element_id not in self.widgets:
            logger.warning(f"Element {element_id} not found in window {self.window_id}")
            return False
        
        widget_entry = self.widgets[element_id]
        
        # Handle composite widgets (stored as dictionaries)
        if isinstance(widget_entry, dict):
            widget = widget_entry.get('widget')
            var = widget_entry.get('var')
        else:
            widget = widget_entry
            var = None
        
        try:
            if property_name == "text":
                if hasattr(widget, 'config'):
                    widget.config(text=str(value))
                elif hasattr(widget, 'configure'):
                    widget.configure(text=str(value))
                return True
            
            elif property_name == "value":
                # For composite widgets with variables
                if var and hasattr(var, 'set'):
                    if isinstance(widget, ttk.Scale):
                        # For sliders, also update the widget itself
                        widget.set(float(value))
                        var.set(str(int(float(value))))  # Update the display
                    else:
                        var.set(value)
                    return True
                # For direct widgets
                elif isinstance(widget, ttk.Scale):
                    widget.set(float(value))
                    return True
                elif isinstance(widget, ttk.Combobox):
                    widget.set(str(value))
                    return True
                elif hasattr(widget, 'set'):
                    widget.set(value)
                    return True
                else:
                    logger.warning(f"Cannot set value for widget type {type(widget)} (element {element_id})")
                    return False
            
            elif property_name == "enabled":
                state = "normal" if value else "disabled"
                if hasattr(widget, 'config'):
                    widget.config(state=state)
                elif hasattr(widget, 'configure'):
                    widget.configure(state=state)
                return True
            
            logger.warning(f"Unknown property {property_name} for element {element_id}")
            return False
            
        except Exception as e:
            logger.error(f"Failed to update element {element_id} property {property_name}: {e}")
            return False

    def get_element_value(self, element_id: str) -> Any:
        """Get the current value of an element"""
        if element_id not in self.widgets:
            logger.warning(f"Element {element_id} not found in window {self.window_id}")
            return None
        
        widget_entry = self.widgets[element_id]
        
        # Handle composite widgets (stored as dictionaries)
        if isinstance(widget_entry, dict):
            widget = widget_entry.get('widget')
            var = widget_entry.get('var')
        else:
            widget = widget_entry
            var = None
        
        try:
            # For composite widgets with variables, prefer the variable
            if var and hasattr(var, 'get'):
                value = var.get()
                # Convert to appropriate type
                if isinstance(widget, ttk.Scale):
                    return float(value) if isinstance(value, str) else value
                elif isinstance(var, tk.BooleanVar):
                    return bool(value)
                else:
                    return value
            # For direct widgets
            elif isinstance(widget, ttk.Scale):
                return widget.get()
            elif isinstance(widget, ttk.Combobox):
                return widget.get()
            elif hasattr(widget, 'get'):
                return widget.get()
            elif hasattr(widget, 'cget') and hasattr(widget, 'config'):
                # Try to get text content for labels, buttons, etc.
                try:
                    return widget.cget('text')
                except:
                    pass
            
            logger.warning(f"Cannot get value for element {element_id} of type {type(widget)}")
            return None
            
        except Exception as e:
            logger.error(f"Failed to get value for element {element_id}: {e}")
            return None
    
    def _on_window_close(self):
        """Handle window close button (X) being clicked for secondary windows"""
        try:
            logger.info(f"Secondary window {self.window_id} close button clicked")
            self.close()
        except Exception as e:
            logger.error(f"Error in window close handler: {e}")
    
    def _on_main_window_close(self):
        """Handle main window close button (X) being clicked"""
        try:
            logger.info(f"Main window {self.window_id} close button clicked - quitting application")
            self._quit_application()
        except Exception as e:
            logger.error(f"Error in main window close handler: {e}")
    
    def _quit_application(self):
        """Quit the entire application properly"""
        try:
            # Close all windows
            global window_registry
            for window_id, window in list(window_registry.items()):
                try:
                    window.close()
                except:
                    pass
            
            # Signal main loop to quit - this should trigger proper asyncio cleanup
            signal_main_loop_quit()
            
        except Exception as e:
            logger.error(f"Error quitting application: {e}")
            # Only force quit as last resort
            signal_main_loop_quit()
    
    def close(self):
        """Close the window"""
        global window_registry
        
        try:
            if self.window:
                self.window.destroy()
                self.window = None
            
            self.created = False
            self.widgets.clear()
            self.callbacks.clear()
            
            if self.window_id in window_registry:
                del window_registry[self.window_id]
            
            # Check if all windows are closed and signal main loop to quit if needed
            if len(window_registry) == 0:
                # All windows closed, signal the main tkinter loop to quit
                logger.info("All windows closed, signaling main loop to quit")
                signal_main_loop_quit()
            
            logger.info(f"UI window {self.window_id} closed")
            
        except Exception as e:
            logger.warning(f"Error closing UI window {self.window_id}: {e}")


def create_native_window(title: str, width: int = 800, height: int = 600) -> UIWindow:
    """Create a new native UI window"""
    window_id = str(uuid.uuid4())
    window = UIWindow(window_id, title, width, height)
    return window


def list_native_windows() -> str:
    """List all native UI windows"""
    if not window_registry:
        return "No native UI windows open"
    
    result = f"Open native UI windows ({len(window_registry)}):\n"
    for window_id, window in window_registry.items():
        status = "created" if window.created else "not created"
        result += f"  {window_id}: '{window.title}' ({status})\n"
    
    return result.rstrip()


def is_native_ui_available() -> bool:
    """Check if native UI is available (always true if tkinter is available)"""
    try:
        import tkinter
        return True
    except ImportError:
        return False


# Convenience functions for CLI compatibility
def create_window(title: str, width: int = 800, height: int = 600) -> str:
    """Create a new window and return its ID"""
    window_id = str(uuid.uuid4())
    window = UIWindow(window_id, title, width, height)
    window.create()
    return window_id

def get_window(window_id: str) -> Optional[UIWindow]:
    """Get window by ID"""
    return window_registry.get(window_id)

def set_window_ui(window_id: str, ui_description: Dict[str, Any]) -> bool:
    """Set UI description for a window"""
    window = get_window(window_id)
    if window:
        window.set_ui(ui_description)
        return True
    return False

def show_window(window_id: str) -> bool:
    """Show a window"""
    window = get_window(window_id)
    if window:
        window.show()
        return True
    return False

def hide_window(window_id: str) -> bool:
    """Hide a window"""
    window = get_window(window_id)
    if window:
        window.hide()
        return True
    return False

def close_window(window_id: str) -> bool:
    """Close a window"""
    window = get_window(window_id)
    if window:
        window.close()
        return True
    return False

def list_windows() -> str:
    """List all open windows"""
    if not window_registry:
        return "No windows open"
    
    windows_info = []
    for window_id, window in window_registry.items():
        status = "created" if window.created else "not created"
        windows_info.append(f"  {window_id}: '{window.title}' ({status})")
    
    return f"Open windows ({len(window_registry)}):\n" + "\n".join(windows_info)


def gui_available() -> bool:
    """Check if GUI is available"""
    return GUI_AVAILABLE


def html_rendering_available() -> bool:
    """Check if HTML rendering is available"""
    return HTML_RENDERING_AVAILABLE


def get_html_engine() -> str:
    """Get the HTML rendering engine name"""
    return HTML_ENGINE


# For backward compatibility, also export HTMLWindow as UIWindow
HTMLWindow = UIWindow
