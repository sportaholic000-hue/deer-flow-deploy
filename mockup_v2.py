"""
Mockup V2 HTML Builder - Premium landing page generation
All 10 visual upgrades: scroll reveals, glassmorphism, hero overhaul,
kinetic stats, hover reveals, testimonial redesign, floating CTA,
background textures, mobile polish, and more.
"""

import urllib.parse

def _svc_desc(svc_name):
    """Generate a brief description for a service card."""
    s = svc_name.lower()
    if 'consult' in s: return 'Expert guidance tailored to your unique situation and goals.'
    if 'emerg' in s: return 'Available around the clock when you need us most.'
    if 'custom' in s: return 'Bespoke solutions designed specifically for your needs.'
    if 'free' in s: return 'No obligation, no pressure. Let us show you what we can do.'
    if 'install' in s: return 'Professional setup done right the first time, guaranteed.'
    if 'repair' in s: return 'Fast, reliable fixes that last. We stand behind our work.'
    if 'clean' in s: return 'Spotless results every time with eco-friendly methods.'
    if 'design' in s: return 'Creative solutions that blend form and function beautifully.'
    return 'Professional, reliable service tailored to exceed your expectations.'


def _avatar_color(name):
    """Generate a consistent hex color from a name string."""
    colors = ['#e63946','#457b9d','#2a9d8f','#e9c46a','#f4a261','#264653','#6a4c93','#1982c4']
    h = 0
    for c in name:
        h = (h * 31 + ord(c)) & 0xFFFFFFFF
    return colors[h % len(colors)]


def _initials(name):
    """Extract initials from an author name like 'Sarah M.'"""
    parts = name.replace('.', '').strip().split()
    if len(parts) >= 2:
        return parts[0][0].upper() + parts[1][0].upper()
    return name[0].upper() if name else '?'


def build_mockup_html(name, city, category, phone, address, website, has_website,
                      accent, bg_gradient, hero_image_url, about_image_url,
                      tagline, about_text, services, reviews, rating, review_count, rating_html):
    """Build a premium self-contained HTML landing page string."""

    # --- Pre-compute data ---
    map_query = urllib.parse.quote((name + ' ' + city) if city else name)
    first_letter = name[0] if name else 'B'
    rest_name = name[1:] if len(name) > 1 else ''

    # Stats values
    stat_rating = str(rating) if rating else '4.9'
    stat_customers = str(review_count) if review_count else '500+'
    stat_customers_num = ''.join(c for c in stat_customers if c.isdigit()) or '500'
    stat_rating_num = stat_rating.replace('.', '') if '.' in stat_rating else stat_rating

    # --- BUILD SERVICE CARDS ---
    service_icons = ['fa-star','fa-cog','fa-check-circle','fa-bolt','fa-heart','fa-gem']
    services_html = ''
    for i, svc in enumerate(services[:6]):
        icon = service_icons[i % len(service_icons)]
        svc_name = svc if isinstance(svc, str) else str(svc)
        desc = _svc_desc(svc_name)
        delay = str(i * 100)
        services_html += (
            '<div class="service-card reveal" data-delay="' + delay + '">'
            '<div class="svc-icon"><i class="fa ' + icon + '"></i></div>'
            '<h3>' + svc_name + '</h3>'
            '<p class="svc-desc">' + desc + '</p>'
            '</div>'
        )

    # --- BUILD REVIEW CARDS ---
    reviews_html = ''
    for j, rev in enumerate(reviews[:3]):
        author = rev.get('author', 'Happy Customer') if isinstance(rev, dict) else 'Happy Customer'
        text = rev.get('text', 'Excellent service!') if isinstance(rev, dict) else str(rev)
        rev_stars = rev.get('stars', 5) if isinstance(rev, dict) else 5
        rev_stars_html = '<i class="fa fa-star"></i>' * int(rev_stars)
        ini = _initials(author)
        acolor = _avatar_color(author)
        delay = str(j * 150)
        reviews_html += (
            '<div class="review-card reveal" data-delay="' + delay + '">'
            '<div class="review-quote-mark">"</div>'
            '<div class="review-stars">' + rev_stars_html + '</div>'
            '<p class="review-text">"' + text + '"</p>'
            '<div class="review-author">'
            '<div class="review-avatar" style="background:' + acolor + ';">' + ini + '</div>'
            '<span>' + author + '</span>'
            '</div></div>'
        )

    # --- CONTACT INFO ---
    contact_details = ''
    if phone:
        contact_details += '<p><i class="fa fa-phone" style="color:' + accent + ';margin-right:10px;"></i> ' + phone + '</p>'
    if address:
        contact_details += '<p><i class="fa fa-map-marker" style="color:' + accent + ';margin-right:10px;"></i> ' + address + '</p>'
    if city:
        contact_details += '<p><i class="fa fa-building" style="color:' + accent + ';margin-right:10px;"></i> ' + city + '</p>'

    # --- CTA BUTTONS ---
    cta_primary = '<a href="tel:' + phone + '" class="cta-btn">Call Now</a>' if phone else '<a href="#contact" class="cta-btn">Get in Touch</a>'
    cta_secondary = '<a href="' + website + '" class="cta-btn-outline" target="_blank">Visit Website</a>' if has_website else ''

    # ===================================================================
    # BUILD THE COMPLETE HTML
    # ===================================================================
    html = '<!DOCTYPE html><html lang="en"><head>'
    html += '<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">'
    html += '<title>' + name + ' | ' + (city or category.title()) + '</title>'
    html += '<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css">'
    html += '<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap" rel="stylesheet">'

    # ============ CSS ============
    html += '<style>'

    # Reset and Base
    html += '*, *::before, *::after { margin:0; padding:0; box-sizing:border-box; }'
    html += 'html { scroll-behavior:smooth; }'
    html += 'body { font-family:"Inter",sans-serif; background:' + bg_gradient + '; color:#e0e0e0; overflow-x:hidden; position:relative; }'
    html += 'a { text-decoration:none; color:inherit; }'

    # Body noise texture overlay
    html += 'body::after { content:""; position:fixed; top:0; left:0; width:100%; height:100%; pointer-events:none; z-index:9999; opacity:0.02; '
    html += 'background-image:url("data:image/svg+xml,%3Csvg viewBox=\'0 0 256 256\' xmlns=\'http://www.w3.org/2000/svg\'%3E%3Cfilter id=\'n\'%3E%3CfeTurbulence type=\'fractalNoise\' baseFrequency=\'0.9\' numOctaves=\'4\' stitchTiles=\'stitch\'/%3E%3C/filter%3E%3Crect width=\'100%25\' height=\'100%25\' filter=\'url(%23n)\'/%3E%3C/svg%3E"); }'

    # Scroll reveal
    html += '.reveal { opacity:0; transform:translateY(30px); transition:opacity 0.6s ease, transform 0.6s ease; }'
    html += '.reveal.visible { opacity:1; transform:translateY(0); }'

    # Keyframes
    html += '@keyframes float-blob-1 { 0%,100% { transform:translate(0,0) scale(1); } 33% { transform:translate(30px,-20px) scale(1.1); } 66% { transform:translate(-20px,15px) scale(0.95); } }'
    html += '@keyframes float-blob-2 { 0%,100% { transform:translate(0,0) scale(1); } 33% { transform:translate(-25px,20px) scale(1.05); } 66% { transform:translate(15px,-25px) scale(0.9); } }'
    html += '@keyframes float-blob-3 { 0%,100% { transform:translate(0,0) scale(1); } 50% { transform:translate(20px,20px) scale(1.08); } }'
    html += '@keyframes bounce-chevron { 0%,100% { transform:translateY(0); opacity:0.6; } 50% { transform:translateY(10px); opacity:1; } }'
    html += '@keyframes pulse-icon { 0%,100% { transform:scale(1); } 50% { transform:scale(1.15); } }'
    html += '@keyframes slide-up-cta { from { transform:translateY(100%); opacity:0; } to { transform:translateY(0); opacity:1; } }'
    html += '@keyframes gradient-shift { 0% { background-position:0% 50%; } 50% { background-position:100% 50%; } 100% { background-position:0% 50%; } }'

    # Nav
    html += '.nav { position:fixed; top:0; left:0; right:0; z-index:1000; padding:18px 40px; display:flex; justify-content:space-between; align-items:center; background:rgba(10,10,10,0.85); backdrop-filter:blur(20px); border-bottom:1px solid rgba(255,255,255,0.05); transition:all 0.3s; }'
    html += '.nav-brand { font-size:1.4rem; font-weight:800; color:#fff; }'
    html += '.nav-brand span { color:' + accent + '; }'
    html += '.nav-links { display:flex; gap:28px; }'
    html += '.nav-links a { color:#aaa; font-weight:500; font-size:0.9rem; transition:color 0.3s; }'
    html += '.nav-links a:hover { color:' + accent + '; }'
    html += '.hamburger { display:none; flex-direction:column; gap:5px; cursor:pointer; padding:5px; }'
    html += '.hamburger span { display:block; width:24px; height:2px; background:#fff; transition:all 0.3s; }'

    # Hero
    html += '.hero { position:relative; min-height:100vh; display:flex; align-items:center; justify-content:center; text-align:center; overflow:hidden; }'
    html += '.hero-bg { position:absolute; inset:0; background:url("' + hero_image_url + '") center/cover no-repeat; z-index:0; }'
    html += '.hero-overlay { position:absolute; inset:0; z-index:1; background:linear-gradient(135deg, rgba(0,0,0,0.7) 0%, rgba(0,0,0,0.4) 50%, rgba(0,0,0,0.8) 100%); }'
    html += '.hero-mesh { position:absolute; inset:0; z-index:1; background:radial-gradient(ellipse at 20% 50%, ' + accent + '15 0%, transparent 50%), radial-gradient(ellipse at 80% 20%, ' + accent + '10 0%, transparent 40%), radial-gradient(ellipse at 50% 80%, ' + accent + '08 0%, transparent 45%); }'
    html += '.hero-blob { position:absolute; border-radius:50%; filter:blur(80px); opacity:0.12; z-index:1; }'
    html += '.hero-blob-1 { width:400px; height:400px; background:' + accent + '; top:10%; left:15%; animation:float-blob-1 12s ease-in-out infinite; }'
    html += '.hero-blob-2 { width:300px; height:300px; background:' + accent + '; top:60%; right:10%; animation:float-blob-2 15s ease-in-out infinite; }'
    html += '.hero-blob-3 { width:250px; height:250px; background:' + accent + '; bottom:20%; left:50%; animation:float-blob-3 10s ease-in-out infinite; }'
    html += '.hero-content { position:relative; z-index:2; max-width:800px; padding:0 20px; }'
    html += '.hero h1 { font-size:3.8rem; font-weight:900; line-height:1.08; margin-bottom:16px; color:#fff; text-shadow:0 0 40px rgba(0,0,0,0.5); }'
    html += '.hero h1 span { color:' + accent + '; text-shadow:0 0 30px ' + accent + '40; }'
    html += '.hero-tagline { font-size:1.3rem; color:#bbb; margin-bottom:10px; font-weight:300; letter-spacing:0.5px; }'
    html += '.hero-rating { margin-top:12px; color:#ffd700; font-size:1.1rem; }'
    html += '.hero-rating span { color:#fff; margin-left:8px; font-weight:600; }'
    html += '.hero-ctas { margin-top:32px; display:flex; gap:15px; justify-content:center; flex-wrap:wrap; }'
    html += '.scroll-chevron { position:absolute; bottom:30px; left:50%; transform:translateX(-50%); z-index:2; animation:bounce-chevron 2s ease-in-out infinite; color:#fff; font-size:1.5rem; opacity:0.6; }'

    # CTA Buttons
    html += '.cta-btn { display:inline-block; padding:15px 38px; background:' + accent + '; color:#000; font-weight:700; font-size:1rem; border-radius:50px; transition:all 0.3s; border:none; cursor:pointer; }'
    html += '.cta-btn:hover { transform:translateY(-3px); box-shadow:0 8px 30px ' + accent + '55; }'
    html += '.cta-btn-outline { display:inline-block; padding:15px 38px; border:2px solid ' + accent + '; color:' + accent + '; font-weight:700; font-size:1rem; border-radius:50px; transition:all 0.3s; }'
    html += '.cta-btn-outline:hover { background:' + accent + '; color:#000; transform:translateY(-3px); }'

    # Stats Bar
    html += '.stats-bar { display:flex; justify-content:center; gap:60px; padding:50px 40px; border-bottom:1px solid rgba(255,255,255,0.05); flex-wrap:wrap; }'
    html += '.stat-item { text-align:center; }'
    html += '.stat-num { font-size:2.8rem; font-weight:900; color:' + accent + '; line-height:1; }'
    html += '.stat-label { font-size:0.9rem; color:#888; margin-top:6px; font-weight:500; text-transform:uppercase; letter-spacing:1px; }'

    # Sections
    html += 'section { padding:90px 40px; max-width:1200px; margin:0 auto; }'
    html += '.section-title { text-align:center; font-size:2.4rem; font-weight:800; color:#fff; margin-bottom:55px; }'
    html += '.section-title span { color:' + accent + '; }'

    # Service Cards
    html += '.services-grid { display:grid; grid-template-columns:repeat(auto-fit, minmax(300px, 1fr)); gap:25px; }'
    html += '.service-card { backdrop-filter:blur(12px); background:rgba(255,255,255,0.06); border:1px solid rgba(255,255,255,0.1); box-shadow:0 8px 32px rgba(0,0,0,0.3); border-radius:16px; padding:35px 25px; text-align:center; transition:all 0.4s ease; overflow:hidden; position:relative; cursor:default; }'
    html += '.service-card:hover { transform:translateY(-6px); border-color:' + accent + '66; box-shadow:0 12px 40px ' + accent + '20; }'
    html += '.svc-icon { font-size:2.2rem; color:' + accent + '; margin-bottom:18px; transition:transform 0.3s; }'
    html += '.service-card:hover .svc-icon { animation:pulse-icon 0.6s ease; }'
    html += '.service-card h3 { font-size:1.1rem; font-weight:700; color:#fff; margin-bottom:8px; }'
    html += '.svc-desc { font-size:0.85rem; color:#999; line-height:1.5; max-height:0; overflow:hidden; transition:max-height 0.4s ease, opacity 0.3s ease; opacity:0; }'
    html += '.service-card:hover .svc-desc { max-height:80px; opacity:1; }'

    # About
    html += '.about-grid { display:grid; grid-template-columns:1fr 1fr; gap:50px; align-items:center; }'
    html += '.about-text p { font-size:1.15rem; line-height:1.9; color:#bbb; }'
    html += '.about-img { border-radius:16px; overflow:hidden; box-shadow:0 8px 32px rgba(0,0,0,0.4); }'
    html += '.about-img img { width:100%; height:400px; object-fit:cover; transition:transform 0.5s; }'
    html += '.about-img:hover img { transform:scale(1.03); }'

    # Review Cards
    html += '.reviews-grid { display:grid; grid-template-columns:repeat(auto-fit, minmax(300px, 1fr)); gap:25px; }'
    html += '.review-card { backdrop-filter:blur(12px); background:rgba(255,255,255,0.06); border:1px solid rgba(255,255,255,0.1); box-shadow:0 8px 32px rgba(0,0,0,0.3); border-radius:16px; padding:30px; position:relative; transition:all 0.4s ease; }'
    html += '.review-card:hover { transform:translateY(-4px) rotateY(2deg); border-color:' + accent + '44; box-shadow:0 12px 40px ' + accent + '15; }'
    html += '.review-quote-mark { font-size:4rem; color:' + accent + '; opacity:0.2; line-height:1; font-family:Georgia,serif; position:absolute; top:15px; left:20px; }'
    html += '.review-stars { color:#ffd700; font-size:0.9rem; margin-bottom:14px; margin-top:10px; }'
    html += '.review-text { font-style:italic; margin-bottom:16px; color:#ccc; line-height:1.7; font-size:0.95rem; }'
    html += '.review-author { display:flex; align-items:center; gap:12px; }'
    html += '.review-avatar { width:40px; height:40px; border-radius:50%; display:flex; align-items:center; justify-content:center; font-weight:700; font-size:0.85rem; color:#fff; }'
    html += '.review-author span { font-weight:600; color:' + accent + '; font-size:0.95rem; }'

    # Contact
    html += '.contact-grid { display:grid; grid-template-columns:1fr 1fr; gap:50px; }'
    html += '.contact-info { display:flex; flex-direction:column; gap:15px; font-size:1.05rem; }'
    html += '.contact-form { display:flex; flex-direction:column; gap:15px; }'
    html += '.contact-form input, .contact-form textarea { padding:15px; border-radius:12px; border:1px solid rgba(255,255,255,0.1); background:rgba(255,255,255,0.05); color:#fff; font-size:1rem; font-family:inherit; transition:border-color 0.3s; }'
    html += '.contact-form input:focus, .contact-form textarea:focus { outline:none; border-color:' + accent + '66; }'

    # Footer
    html += '.footer { text-align:center; padding:30px; color:#555; font-size:0.85rem; border-top:1px solid rgba(255,255,255,0.05); }'

    # Floating CTA Bar
    html += '.floating-cta { position:fixed; bottom:0; left:0; right:0; z-index:999; padding:14px 30px; display:flex; align-items:center; justify-content:center; gap:20px; backdrop-filter:blur(20px); background:rgba(10,10,10,0.9); border-top:1px solid rgba(255,255,255,0.08); transform:translateY(100%); transition:transform 0.4s ease; }'
    html += '.floating-cta.show { transform:translateY(0); }'
    html += '.floating-cta-name { font-weight:700; color:#fff; font-size:0.95rem; }'
    html += '.floating-cta-phone { color:#aaa; font-size:0.9rem; }'
    html += '.floating-cta .cta-btn { padding:10px 28px; font-size:0.9rem; }'

    # Mobile Responsive
    html += '@media (max-width:768px) {'
    html += '  .hero h1 { font-size:2.4rem; }'
    html += '  .about-grid, .contact-grid { grid-template-columns:1fr; }'
    html += '  .nav-links { display:none; position:absolute; top:100%; left:0; right:0; flex-direction:column; background:rgba(10,10,10,0.95); backdrop-filter:blur(20px); padding:20px 40px; gap:15px; border-bottom:1px solid rgba(255,255,255,0.05); }'
    html += '  .nav-links.open { display:flex; }'
    html += '  .hamburger { display:flex; }'
    html += '  section { padding:60px 20px; }'
    html += '  .stats-bar { gap:30px; padding:40px 20px; }'
    html += '  .stat-num { font-size:2rem; }'
    html += '  .services-grid, .reviews-grid { grid-template-columns:1fr; }'
    html += '  .hero-blob { display:none; }'
    html += '  .floating-cta { gap:10px; padding:12px 15px; }'
    html += '  .floating-cta-name { display:none; }'
    html += '  .cta-btn, .cta-btn-outline { padding:12px 28px; min-height:48px; display:flex; align-items:center; justify-content:center; }'
    html += '}'

    html += '</style></head><body>'

    # ============ NAV ============
    html += '<nav class="nav">'
    html += '<div class="nav-brand"><span>' + first_letter + '</span>' + rest_name + '</div>'
    html += '<div class="nav-links">'
    html += '<a href="#services">Services</a><a href="#about">About</a><a href="#reviews">Reviews</a><a href="#contact">Contact</a>'
    html += '</div>'
    html += '<div class="hamburger" onclick="document.querySelector(\'.nav-links\').classList.toggle(\'open\')">'
    html += '<span></span><span></span><span></span>'
    html += '</div>'
    html += '</nav>'

    # ============ HERO ============
    html += '<section class="hero">'
    html += '<div class="hero-bg"></div>'
    html += '<div class="hero-overlay"></div>'
    html += '<div class="hero-mesh"></div>'
    html += '<div class="hero-blob hero-blob-1"></div>'
    html += '<div class="hero-blob hero-blob-2"></div>'
    html += '<div class="hero-blob hero-blob-3"></div>'
    html += '<div class="hero-content">'
    html += '<h1><span>' + name + '</span></h1>'
    html += '<p class="hero-tagline">' + tagline + '</p>'
    html += rating_html
    html += '<div class="hero-ctas">' + cta_primary + cta_secondary + '</div>'
    html += '</div>'
    html += '<div class="scroll-chevron"><i class="fa fa-chevron-down"></i></div>'
    html += '</section>'

    # ============ STATS BAR ============
    html += '<div class="stats-bar reveal">'
    html += '<div class="stat-item"><div class="stat-num" data-target="' + stat_rating_num + '" data-decimal="true">' + stat_rating + '</div><div class="stat-label"><i class="fa fa-star" style="color:#ffd700;margin-right:4px;"></i> Rating</div></div>'
    html += '<div class="stat-item"><div class="stat-num" data-target="' + stat_customers_num + '">' + stat_customers + '</div><div class="stat-label">Happy Customers</div></div>'
    html += '<div class="stat-item"><div class="stat-num" data-target="10">10+</div><div class="stat-label">Years Experience</div></div>'
    html += '</div>'

    # ============ SERVICES ============
    html += '<section id="services">'
    html += '<h2 class="section-title reveal">What We <span>Offer</span></h2>'
    html += '<div class="services-grid">' + services_html + '</div>'
    html += '</section>'

    # ============ ABOUT ============
    html += '<section id="about">'
    html += '<h2 class="section-title reveal">About <span>' + name + '</span></h2>'
    html += '<div class="about-grid">'
    html += '<div class="about-text reveal"><p>' + about_text + '</p></div>'
    html += '<div class="about-img reveal" data-delay="200"><img src="' + about_image_url + '" alt="About ' + name + '" loading="lazy"></div>'
    html += '</div></section>'

    # ============ REVIEWS ============
    html += '<section id="reviews">'
    html += '<h2 class="section-title reveal">What People <span>Say</span></h2>'
    html += '<div class="reviews-grid">' + reviews_html + '</div>'
    html += '</section>'

    # ============ CONTACT ============
    html += '<section id="contact">'
    html += '<h2 class="section-title reveal">Get In <span>Touch</span></h2>'
    html += '<div class="contact-grid reveal">'
    html += '<div class="contact-info">' + contact_details
    html += '<iframe src="https://www.google.com/maps?q=' + map_query + '&output=embed" width="100%" height="300" style="border:0;border-radius:12px;margin-top:10px;" allowfullscreen="" loading="lazy"></iframe>'
    html += '</div>'
    html += '<div class="contact-form">'
    html += '<input type="text" placeholder="Your Name">'
    html += '<input type="email" placeholder="Your Email">'
    html += '<input type="tel" placeholder="Your Phone">'
    html += '<textarea rows="4" placeholder="How can we help?"></textarea>'
    html += '<button type="submit" class="cta-btn" style="text-align:center;">Send Message</button>'
    html += '</div>'
    html += '</div></section>'

    # ============ FOOTER ============
    html += '<footer class="footer">'
    html += '<p>&copy; 2025 ' + name + '. All rights reserved.</p>'
    html += '</footer>'

    # ============ FLOATING CTA BAR ============
    html += '<div class="floating-cta" id="floatingCta">'
    html += '<span class="floating-cta-name">' + name + '</span>'
    if phone:
        html += '<span class="floating-cta-phone"><i class="fa fa-phone" style="margin-right:5px;"></i>' + phone + '</span>'
        html += '<a href="tel:' + phone + '" class="cta-btn">Call Now</a>'
    else:
        html += '<a href="#contact" class="cta-btn">Get in Touch</a>'
    html += '</div>'

    # ============ JAVASCRIPT ============
    html += '<script>'

    # IntersectionObserver for scroll reveals
    html += 'document.addEventListener("DOMContentLoaded",function(){'
    html += 'var reveals=document.querySelectorAll(".reveal");'
    html += 'var observer=new IntersectionObserver(function(entries){'
    html += 'entries.forEach(function(entry){'
    html += 'if(entry.isIntersecting){'
    html += 'var delay=entry.target.getAttribute("data-delay")||0;'
    html += 'setTimeout(function(){entry.target.classList.add("visible");},parseInt(delay));'
    html += 'observer.unobserve(entry.target);'
    html += '}'
    html += '});'
    html += '},{threshold:0.15});'
    html += 'reveals.forEach(function(el){observer.observe(el);});'

    # Counter animation for stats
    html += 'var statObs=new IntersectionObserver(function(entries){'
    html += 'entries.forEach(function(entry){'
    html += 'if(entry.isIntersecting){'
    html += 'var nums=entry.target.querySelectorAll(".stat-num[data-target]");'
    html += 'nums.forEach(function(el){'
    html += 'var target=parseInt(el.getAttribute("data-target"));'
    html += 'var isDec=el.getAttribute("data-decimal")==="true";'
    html += 'var start=0;var duration=2000;var startTime=null;'
    html += 'function animate(ts){'
    html += 'if(!startTime)startTime=ts;'
    html += 'var progress=Math.min((ts-startTime)/duration,1);'
    html += 'var eased=1-Math.pow(1-progress,3);'
    html += 'var current=Math.floor(eased*target);'
    html += 'if(isDec){el.textContent=(current/10).toFixed(1);}else{el.textContent=current+(target>=100?"+":"");}'
    html += 'if(progress<1)requestAnimationFrame(animate);'
    html += '}'
    html += 'requestAnimationFrame(animate);'
    html += '});'
    html += 'statObs.unobserve(entry.target);'
    html += '}'
    html += '});'
    html += '},{threshold:0.3});'
    html += 'var sb=document.querySelector(".stats-bar");if(sb)statObs.observe(sb);'

    # Floating CTA show/hide on scroll
    html += 'var floatingCta=document.getElementById("floatingCta");'
    html += 'window.addEventListener("scroll",function(){'
    html += 'if(window.scrollY>500){floatingCta.classList.add("show");}else{floatingCta.classList.remove("show");}'
    html += '});'

    html += '});'
    html += '</script>'

    html += '</body></html>'

    return html
