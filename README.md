# nicolasleao.github.io
- This is my personal blog, it's completely static, hosted on GitHub.
- All my blog posts are simply markdown files with the slug filename inside the /src/ folder that get rendered into html by my publish script.
- All rendered blog content is in the /posts directory
- all static assets like images are in the /assets directory

### Features include
- syntax highlighting using highlight.js
- full markdown support with tables and all the good stuff
- a manage.py utility that builds my markdown files into html static seo-optimized pages for the web
- everytime a new post is rendered, the page get's the date and timestamp and a new row is added to index.html with a link to that new post
- index.html has an infinite scroll pagination entirely in the frontend to optimize the loadtime of the page