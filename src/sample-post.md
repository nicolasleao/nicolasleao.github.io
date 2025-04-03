# Sample Markdown Post

This is a sample post written in markdown format to test our conversion script. Markdown is a lightweight markup language that you can use to add formatting elements to plaintext text documents.

## Basic Formatting

You can use **bold** and *italic* text, or even ***bold and italic*** together. You can also use ~~strikethrough~~ text.

## Code Examples

Here's an example of inline code: `print("Hello World")`.

And here's a code block with syntax highlighting:

```python
def greet(name):
    """Simple greeting function"""
    return f"Hello, {name}!"
    
if __name__ == "__main__":
    message = greet("Markdown")
    print(message)
```

JavaScript example:

```javascript
function calculateTotal(items) {
    return items.reduce((total, item) => {
        return total + item.price * item.quantity;
    }, 0);
}

const cart = [
    { name: "Product 1", price: 10, quantity: 2 },
    { name: "Product 2", price: 15, quantity: 1 },
    { name: "Product 3", price: 5, quantity: 3 }
];

console.log(`Total: $${calculateTotal(cart)}`);
```

## Lists

Unordered list:

- Item 1
- Item 2
- Item 3
  - Nested item 1
  - Nested item 2

Ordered list:

1. First item
2. Second item
3. Third item

## Tables

| Name     | Type    | Description            |
|----------|---------|------------------------|
| id       | Integer | Unique identifier      |
| title    | String  | Post title             |
| content  | Text    | Post content           |
| created  | Date    | Creation timestamp     |

## Blockquotes

> This is a blockquote.
> It can span multiple lines.
>
> Even multiple paragraphs if you add a blank line.

## Links and Images

[Visit GitHub](https://github.com)

![Sample Image](https://placehold.co/600x400)

## Horizontal Rule

---

That's it for this sample post! The markdown converter should handle all these elements correctly. 