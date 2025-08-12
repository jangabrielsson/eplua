# HTML Widget Upgrade Guide: Switching to tkhtmlview

## 🎯 Problem Statement

The current homemade HTML renderer (`SimpleHTMLLabel`) has significant limitations:
- ❌ Only supports 3 colors (red, blue, green)
- ❌ Limited HTML tag support
- ❌ No hex color support (#FF5733)
- ❌ No RGB/HSL color support
- ❌ Requires manual maintenance for new features
- ❌ Users will encounter unsupported tags/colors

## 🚀 Recommended Solution: tkhtmlview

**tkhtmlview** is a mature Python library that provides full HTML/CSS rendering for tkinter applications.

### ✅ Advantages

1. **Complete Color Support**
   - Named colors: `red`, `blue`, `green`, `purple`, `orange`, `yellow`, `pink`, etc.
   - Hex colors: `#FF5733`, `#33FF57`, `#3357FF`
   - RGB colors: `rgb(255, 87, 51)`, `rgba(255, 87, 51, 0.5)`
   - HSL colors: `hsl(240, 100%, 50%)`

2. **Full HTML/CSS Support**
   - All standard HTML tags: `<h1>`, `<p>`, `<div>`, `<span>`, `<ul>`, `<li>`, etc.
   - CSS styling: `font-size`, `background-color`, `border`, `padding`, etc.
   - Advanced features: gradients, shadows, borders, etc.

3. **Easy Integration**
   - Drop-in replacement for `SimpleHTMLLabel`
   - Minimal code changes required
   - Same API pattern

4. **Maintenance**
   - Actively maintained library
   - No need to implement new HTML features manually
   - Community support and bug fixes

## 📦 Installation

```bash
pip install tkhtmlview
```

Dependencies:
- `Pillow>=10,<11`
- `requests>=2.28.2,<3.0.0`

## 🔧 Integration Steps

### Step 1: Update gui.py

Replace the HTML label creation in `src/eplua/gui.py`:

```python
# Current implementation
if html and HTML_RENDERING_AVAILABLE:
    try:
        label = SimpleHTMLLabel(parent, text, height=1, width=30,
                                borderwidth=0, relief=tk.FLAT)
        label.pack(side=tk.LEFT, padx=(0, 10))
        label.text_widget._html_label_parent = label
        self.widgets[element_id] = label.text_widget
    except Exception as e:
        # Fallback...

# New implementation with tkhtmlview
if html and TKHTMLVIEW_AVAILABLE:
    try:
        from tkhtmlview import HTMLLabel
        label = HTMLLabel(parent, html=text)
        label.pack(side=tk.LEFT, padx=(0, 10))
        self.widgets[element_id] = label
    except Exception as e:
        # Fallback to SimpleHTMLLabel...
```

### Step 2: Update setText Method

Modify the `set_value` method to handle tkhtmlview widgets:

```python
def set_value(self, element_id: str, value: Any):
    """Set the value of an element"""
    if element_id not in self.widgets:
        return

    widget_info = self.widgets[element_id]

    # Handle tkhtmlview HTMLLabel
    if hasattr(widget_info, 'set_html'):
        widget_info.set_html(str(value))
        logger.info(f"Updated tkhtmlview label {element_id}")
    # Handle our SimpleHTMLLabel (fallback)
    elif isinstance(widget_info, tk.Text) and hasattr(widget_info, '_html_label_parent'):
        widget_info._html_label_parent.render_html(str(value))
        logger.info(f"Updated SimpleHTMLLabel {element_id}")
    # ... rest of existing code
```

### Step 3: Add Import and Availability Check

At the top of `src/eplua/gui.py`:

```python
# Import tkhtmlview support
try:
    from tkhtmlview import HTMLLabel
    TKHTMLVIEW_AVAILABLE = True
    HTML_ENGINE = "tkhtmlview"
    logger.info("tkhtmlview is available for enhanced HTML rendering")
except ImportError:
    TKHTMLVIEW_AVAILABLE = False
    # Keep existing SimpleHTMLLabel fallback
```

### Step 4: Update Dependencies

Add to `pyproject.toml`:

```toml
[project]
dependencies = [
    # ... existing dependencies
    "tkhtmlview>=0.3.0",
]
```

## 🧪 Testing

### Test HTML Features

```lua
-- Test enhanced colors
{
    type = "label",
    text = "<span style='color: purple;'>Purple</span> <span style='color: #FF5733;'>Hex Color</span>",
    html = true,
    id = "enhanced_colors"
}

-- Test advanced styling
{
    type = "label", 
    text = "<div style='border: 2px solid blue; padding: 10px; background-color: lightgray;'>Styled Box</div>",
    html = true,
    id = "styled_box"
}

-- Test font sizes
{
    type = "label",
    text = "<span style='font-size: 24px; color: red;'>Large Red Text</span>",
    html = true,
    id = "large_text"
}
```

## 🔄 Migration Strategy

### Phase 1: Add tkhtmlview Support (Backward Compatible)
1. Install tkhtmlview as optional dependency
2. Add tkhtmlview support with SimpleHTMLLabel fallback
3. Test existing HTML labels continue to work
4. Test new HTML features work with tkhtmlview

### Phase 2: Deprecate SimpleHTMLLabel
1. Update documentation to recommend tkhtmlview features
2. Add deprecation warnings for limited color usage
3. Provide migration examples

### Phase 3: Make tkhtmlview Default
1. Make tkhtmlview a required dependency
2. Keep SimpleHTMLLabel as fallback only
3. Update all examples to use enhanced HTML

## 📊 Comparison

| Feature | SimpleHTMLLabel | tkhtmlview |
|---------|----------------|------------|
| Colors | 3 (red, blue, green) | All HTML colors |
| Hex Colors | ❌ | ✅ |
| RGB Colors | ❌ | ✅ |
| Font Sizes | 3 (big, normal, small) | Any CSS size |
| Background Colors | ❌ | ✅ |
| Borders | ❌ | ✅ |
| Advanced CSS | ❌ | ✅ |
| Maintenance | Manual | Library maintained |
| File Size | Small | Larger (with dependencies) |

## 🎨 Example Enhancements

With tkhtmlview, users can now use:

```html
<!-- Rich color palette -->
<span style="color: purple;">Purple text</span>
<span style="color: #FF5733;">Hex color</span>
<span style="color: rgb(255, 87, 51);">RGB color</span>

<!-- Background colors -->
<span style="background-color: yellow; padding: 5px;">Highlighted text</span>

<!-- Advanced styling -->
<div style="border: 2px solid #333; padding: 10px; border-radius: 5px; background: linear-gradient(45deg, #ff6b6b, #4ecdc4);">
    Styled container with gradient background
</div>

<!-- Precise font control -->
<span style="font-size: 18px; font-weight: bold; text-shadow: 1px 1px 2px gray;">
    Advanced typography
</span>
```

## 🚀 Recommendation

**Switch to tkhtmlview immediately** for the following reasons:

1. **User Experience**: No more "unsupported color/tag" issues
2. **Developer Experience**: No more manual HTML feature implementation
3. **Future-Proof**: Leverages standard HTML/CSS instead of custom parsing
4. **Minimal Risk**: Fallback to SimpleHTMLLabel ensures compatibility
5. **Easy Migration**: Drop-in replacement with enhanced capabilities

The benefits far outweigh the small dependency cost, and users will appreciate the dramatically improved HTML support.
