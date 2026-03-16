export default defineEventHandler((event) => {
  const config = useRuntimeConfig()
  const siteUrl = config.public.siteUrl || 'http://localhost:3000'

  // Basic static routes - add more routes or dynamic generation as needed
  const routes = ['/', '/committee', '/news-events', '/yogam']

  const urls = routes
    .map((r) => `  <url>\n    <loc>${siteUrl}${r}</loc>\n    <changefreq>weekly</changefreq>\n    <priority>0.7</priority>\n  </url>`)
    .join('\n')

  const xml = `<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n${urls}\n</urlset>`

  setHeader(event, 'content-type', 'application/xml')
  return xml
})
