# Personal Blog System

A simple static blog system that converts markdown files to HTML using templates.

## How It Works

1. Write your posts as markdown files in the `src/` directory
2. Run the build script to convert them to HTML in the `posts/` directory
3. The script also updates the index.html with links to new posts

## Versioning System

The blog uses a versioning system to track changes to the template and ensure consistent styling:

- `post-data.json` tracks the current app version and information about each post
- When the template changes, update the app version and all posts will be updated to match

## Commands

### Build posts

```bash
python manage.py build
```

### Force rebuild all posts

```bash
python manage.py build --force
```

### Update app version

```bash
python manage.py version 1.0.1
```

### Regenerate all posts using the current template

```bash
python manage.py regenerate
```

## Workflow Example

1. Create markdown files in the `src/` directory
2. Run `python manage.py build` to generate HTML files
3. Make changes to the template (`posts/_template.html`)
4. Run `python manage.py version 1.0.1` to update the app version
5. Run `python manage.py build` to update all posts with different versions
6. To force update all posts regardless of version, use `python manage.py regenerate`

## Project Structure

- `src/`: Markdown source files
- `posts/`: Generated HTML posts
- `posts/_template.html`: HTML template for posts
- `index.html`: Main blog index
- `index.js`: JavaScript for the site
- `styles.css`: CSS styles
- `post-data.json`: Version tracking
- `manage.py`: Build script
