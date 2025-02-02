// Throttle function
function throttle(func, limit) {
    let inThrottle;
    return function() {
        const args = arguments;
        const context = this;
        if (!inThrottle) {
            func.apply(context, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    }
}

// Initialize AOS
AOS.init({
    duration: 800,
    easing: 'ease-in-out',
    once: true
});

// Smooth scrolling with snap
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const targetId = this.getAttribute('href');
        const targetSection = document.querySelector(targetId);

        if (targetSection) {
            targetSection.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });

            // Update URL without scrolling
            history.pushState(null, null, targetId);
        }
    });
});

// Navbar and back-to-top button scroll effect
window.addEventListener('scroll', throttle(function() {
    const navbar = document.querySelector('.navbar');
    const backToTop = document.querySelector('.back-to-top');
    
    if (window.scrollY > 50) {
        navbar.style.background = 'rgba(10, 25, 47, 0.98)';
        navbar.style.boxShadow = '0 0 10px rgba(0, 0, 0, 0.3)';
        if (backToTop) backToTop.style.opacity = '1';
    } else {
        navbar.style.background = 'rgba(10, 25, 47, 0.1)';
        navbar.style.boxShadow = 'none';
        if (backToTop) backToTop.style.opacity = '0.5';
    }
}, 100));

// Active section highlighting
window.addEventListener('scroll', throttle(function() {
    let sections = document.querySelectorAll('section');
    let navLinks = document.querySelectorAll('.nav-link');
    
    sections.forEach(section => {
        let top = section.offsetTop - 100;
        let bottom = top + section.offsetHeight;
        let scroll = window.scrollY;
        let id = section.getAttribute('id');
        
        if (scroll >= top && scroll < bottom) {
            navLinks.forEach(link => {
                link.classList.remove('active');
                if (link.getAttribute('href') === '#' + id) {
                    link.classList.add('active');
                }
            });
        }
    });
}, 100));

// Modal handling for projects
function openProjectModal(title, description, image) {
    const modal = document.getElementById('projectModal');
    modal.querySelector('.modal-title').textContent = title;
    modal.querySelector('.modal-body').innerHTML = `
        <img src="${image}" class="img-fluid mb-3" alt="${title}">
        <p>${description}</p>
    `;
    new bootstrap.Modal(modal).show();
}

// Modal handling for skills
function openSkillModal(title, description) {
    const modal = document.getElementById('skillModal');
    modal.querySelector('.modal-title').textContent = title;
    modal.querySelector('.modal-body').innerHTML = `<p>${description}</p>`;
    new bootstrap.Modal(modal).show();
}

// Prevent dropdown from closing when clicking inside
document.querySelector('.dropdown-menu').addEventListener('click', function(e) {
    e.stopPropagation();
});

// Hamburger menu functionality
const hamburgerMenu = document.getElementById('hamburger-icon');
const navbarNav = document.getElementById('navbarNav');

hamburgerMenu.addEventListener('click', function() {
    this.classList.toggle('active');
    const dropdownMenu = document.querySelector('.dropdown-menu');
    dropdownMenu.classList.toggle('show');
});

// Close menu when clicking outside
document.addEventListener('click', function(event) {
    const isClickInside = hamburgerMenu.contains(event.target) || navbarNav.contains(event.target);
    
    if (!isClickInside && hamburgerMenu.classList.contains('active')) {
        hamburgerMenu.classList.remove('active');
        document.querySelector('.dropdown-menu').classList.remove('show');
    }
});

// Close menu when clicking a link
document.querySelectorAll('.dropdown-item').forEach(item => {
    item.addEventListener('click', function() {
        hamburgerMenu.classList.remove('active');
        document.querySelector('.dropdown-menu').classList.remove('show');
    });
});

// Project details data
const projectDetails = [
    {
        title: "Portfolio Website",
        image: "/static/images/CarouselPreview1.jpg",
        content: `
            <h3>Portfolio Website Development</h3>
            <p>This personal portfolio website was built from scratch using HTML, CSS, JavaScript, and the Flask web framework; all standard fare for web development. The twist? I began without knowing a single line of HTML code.</p>

            <p>The project started as an experiment to demonstrate how effectively Large Language Models (LLMs) could assist in developing production-ready code in completely unfamiliar domains.</p>
            <p>I wanted to prove that with the help of these LLMs, a complete layman could build a custom, fully functional website from scratch in a short span of time. Incidentally, I have also built a simple video editing web app the same way.</p>
            <p>My next project will be (tentatively) an Android/iOS app.</p>

            <h4>Key Features</h4>
            <ul>
                <li>Underwater themed personal portfolio</li>
                <li>Works on both desktop and mobile</li>
                <li>Interactive particle animations</li>
                <li>Custom carousel implementation with dynamic content loading</li>
                <li>CSS animations and transitions</li>
                <li>Modal implementations for project details</li>
                <li>Integration with Flask backend</li>
            </ul>

            <h4>Development Tools</h4>
            <ul>
                <li>Frontend: HTML5, CSS3, JavaScript (ES6+)</li>
                <li>Backend: Python (Flask)</li>
                <li>Framework: Bootstrap 5</li>
                <li>Libraries: Particles.js, AOS, Typed.js</li>
                <li>Development Environment: Replit</li>
                <li>AI Assistance: Replit Agent, Anthropic's Claude, OpenAI's ChatGPT</li>
            </ul>

            <div style="margin-top: 0.5rem; padding-top: 0.5rem; border-top: 1px solid rgba(255,255,255,0.1);">
                <a href="https://github.com/Aghbuul/Portfolio-Website" target="_blank" style="color: #64ffda; text-decoration: none; display: flex; align-items: center; justify-content: center; gap: 0.5rem; padding: 0.375rem 0;">
                    <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 19c-5 1.5-5-2.5-7-3m14 6v-3.87a3.37 3.37 0 0 0-.94-2.61c3.14-.35 6.44-1.54 6.44-7A5.44 5.44 0 0 0 20 4.77 5.07 5.07 0 0 0 19.91 1S18.73.65 16 2.48a13.38 13.38 0 0 0-7 0C6.27.65 5.09 1 5.09 1A5.07 5.07 0 0 0 5 4.77a5.44 5.44 0 0 0-1.5 3.78c0 5.42 3.3 6.61 6.44 7A3.37 3.37 0 0 0 9 18.13V22"></path></svg>
                    View on GitHub
                </a>
            </div>
            `
    },
    {
        title: "Disease Modelling App",
        image: "/static/images/CarouselPreview2.jpg",
        content: `
            <h3>SEIR Disease Modelling Application</h3>
            <p>This R Shiny application provides an interactive interface for exploring epidemiological models, specifically focusing on the SEIR (Susceptible-Exposed-Infected-Recovered) model dynamics.</p>

            <h4>Technical Implementation</h4>
            <p>Built using R Shiny, the application solves differential equations in real-time, allowing users to manipulate parameters and instantly see their effects on disease spread patterns.</p>

            <h4>Features</h4>
            <ul>
                <li>Real-time parameter adjustment</li>
                <li>Interactive visualizations</li>
                <li>Multiple scenario comparison</li>
                <li>Data export capabilities</li>
            </ul>

            <p>This project combines epidemiological theory with practical application, making complex mathematical models accessible to non-technical users.</p>
    <div style="margin-top: 2rem; padding-top: 1rem; border-top: 1px solid rgba(255,255,255,0.1);">
        <a href="https://github.com/Aghbuul/interactive-seir-app" target="_blank" style="color: #64ffda; text-decoration: none; display: flex; align-items: center; justify-content: center; gap: 0.5rem;">
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 19c-5 1.5-5-2.5-7-3m14 6v-3.87a3.37 3.37 0 0 0-.94-2.61c3.14-.35 6.44-1.54 6.44-7A5.44 5.44 0 0 0 20 4.77 5.07 5.07 0 0 0 19.91 1S18.73.65 16 2.48a13.38 13.38 0 0 0-7 0C6.27.65 5.09 1 5.09 1A5.07 5.07 0 0 0 5 4.77a5.44 5.44 0 0 0-1.5 3.78c0 5.42 3.3 6.61 6.44 7A3.37 3.37 0 0 0 9 18.13V22"></path></svg>
            View on GitHub
        </a>
    </div>`        
    },
    {
        title: "Pixel Art Generator",
        image: "/static/images/CarouselPreview4.jpg",
        content: `
            <h3>Pixel Art Generator</h3>
            <p>A web-based tool for creating pixel art animations and sprite sheets, built entirely from scratch using JavaScript and HTML5's Canvas technology.</p>

            <p>At its core, the application uses multiple Canvas elements (essentially digital drawing boards built into web browsers) to process images in real-time. It features a unique overlay system that allows users to combine images and create complex animations; Similar to how layers work in Photoshop, but running entirely in your browser.</p>

            <h4>Key Features</h4>
            <ul>
                <li>Real-time pixel art transformation: Transform any image into pixel art by automatically reducing its detail level, with precise control over the pixelation amount</li>
                <li>Smart overlay system: Add images on top of your pixel art with adjustable transparency and automatic white background removal</li>
                <li>Animation creation: Build animations frame by frame, or automatically generate transition frames between different pixelation levels</li>
                <li>Sprite sheet generation: Automatically compile your animation frames into a single image sheet - a format commonly used in game development</li>
                <li>Video export: Convert your animations directly into video files using your browser's built-in recording capabilities</li>
                <li>User-friendly interface: Features dark mode and customizable keyboard shortcuts for efficient workflow</li>
            </ul>

            <h4>Technical Implementation</h4>
            <ul>
                <li>Core Technology: Built using JavaScript and HTML5 Canvas - a browser technology that allows pixel-by-pixel manipulation of images</li>
                <li>Image Processing: Implements custom pixel manipulation techniques including:
                    - A sampling algorithm that groups pixels together to create the pixelation effect
                    - Color analysis algorithms that can detect and remove white backgrounds from overlays
                    - Frame interpolation that creates smooth transitions between animation states</li>
                <li>Animation System: Uses the browser's RequestAnimationFrame API (a built-in timing tool that synchronizes animations with screen refresh rates) to ensure smooth playback</li>
                <li>Video Creation: Uses the MediaRecorder API (a built-in browser tool for creating video files) to export animations as standard web-compatible videos</li>
                <li>User Interface: Custom-built interface using modern CSS features including:
                    - CSS Variables for dynamic theme switching
                    - CSS Grid for responsive layouts
                    - CSS Transitions for smooth interface animations</li>
                <li>Additional Tools: Integrates Feather Icons (an open-source icon set) for a polished, professional look</li>
            </ul>

            <p>The logo and background arts were all generated using Google's Veo 2.</p>


            <div style="margin-top: 1rem; padding-top: 0.5rem; border-top: 1px solid rgba(255,255,255,0.1);">
    <a href="https://pixel-art-generator.replit.app" target="_blank" style="color: #64ffda; text-decoration: none; display: flex; align-items: center; justify-content: center; gap: 0.5rem; padding: 0.375rem 0;">
        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h7"></path><line x1="16" y1="5" x2="22" y2="5"></line><line x1="22" y1="5" x2="22" y2="11"></line><line x1="16" y1="5" x2="22" y2="11"></line></svg>
        Try Now
    </a>
</div>

<div style="margin-top: 0.5rem; padding-top: 0.5rem; border-top: 1px solid rgba(255,255,255,0.1);">
    <a href="https://github.com/Aghbuul/pixelcraft-studio" target="_blank" style="color: #64ffda; text-decoration: none; display: flex; align-items: center; justify-content: center; gap: 0.5rem; padding: 0.375rem 0;">
        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 19c-5 1.5-5-2.5-7-3m14 6v-3.87a3.37 3.37 0 0 0-.94-2.61c3.14-.35 6.44-1.54 6.44-7A5.44 5.44 0 0 0 20 4.77 5.07 5.07 0 0 0 19.91 1S18.73.65 16 2.48a13.38 13.38 0 0 0-7 0C6.27.65 5.09 1 5.09 1A5.07 5.07 0 0 0 5 4.77a5.44 5.44 0 0 0-1.5 3.78c0 5.42 3.3 6.61 6.44 7A3.37 3.37 0 0 0 9 18.13V22"></path></svg>
        View on GitHub
    </a>
</div>`
    },
    {
        title: "Anime Sigil Eyes",
        image: "/static/images/CarouselPreview5.jpg",
        content: `
            <h3>Anime Sigil Eyes</h3>
            <p>A sophisticated web application that leverages machine learning - specifically, Google's MediaPipe Face Mesh - for precise facial landmark detection. It automatically detects eyes in an uploaded image to overlay customisable sigils onto eyes in photographs.</p>
            <p>You can try it <a href="https://anime-eyes.replit.app/" target="_blank" style="color: #64ffda; text-decoration: underline;">here</a>.</p>
            

            <h4>Face Detection Pipeline</h4>
            <ul>
                <li>Implements Google's MediaPipe Face Mesh (Apache 2.0 license)</li>
                <li>Detects 468 facial landmarks at 30+ FPS</li>
                <li>Utilises landmarks 468/473 for precise eye centre detection</li>
                <li>Client-side ML processing for privacy and performance</li>
                <li>Real-time landmark tracking with sub-pixel accuracy</li>
            </ul>

            <h4>Development Stack</h4>
            <ul>
                <li>Frontend: React 18.3 with TypeScript, Vite build system, TailwindCSS + shadcn/ui components</li>
                <li>Backend: Express.js with TypeScript, PostgreSQL + Drizzle ORM, RESTful API architecture</li>
            </ul>

            <h4>Technical Features</h4>
            <ul>
                <li>Drag-and-drop interface with synthetic event handling</li>
                <li>Independent transform controls per sigil</li>
                <li>Real-time preview system</li>
                <li>Cross-browser compatibility layer</li>
            </ul>

            <p>This was developed with heavy assistance from Replit Agent and Anthropic's Claude. Special thanks to my friend who told me to "Just talk to [Claude] like you hired an engineer" for inspiring me.</p>

            <div style="margin-top: 1rem; padding-top: 0.5rem; border-top: 1px solid rgba(255,255,255,0.1);">
    <a href="https://anime-eyes.replit.app/" target="_blank" style="color: #64ffda; text-decoration: none; display: flex; align-items: center; justify-content: center; gap: 0.5rem; padding: 0.375rem 0;">
        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h7"></path><line x1="16" y1="5" x2="22" y2="5"></line><line x1="22" y1="5" x2="22" y2="11"></line><line x1="16" y1="5" x2="22" y2="11"></line></svg>
        Try Now
    </a>
</div>

<div style="margin-top: 0.5rem; padding-top: 0.5rem; border-top: 1px solid rgba(255,255,255,0.1);">
    <a href="https://github.com/Aghbuul/Anime-Sigil-Eyes" target="_blank" style="color: #64ffda; text-decoration: none; display: flex; align-items: center; justify-content: center; gap: 0.5rem; padding: 0.375rem 0;">
        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 19c-5 1.5-5-2.5-7-3m14 6v-3.87a3.37 3.37 0 0 0-.94-2.61c3.14-.35 6.44-1.54 6.44-7A5.44 5.44 0 0 0 20 4.77 5.07 5.07 0 0 0 19.91 1S18.73.65 16 2.48a13.38 13.38 0 0 0-7 0C6.27.65 5.09 1 5.09 1A5.07 5.07 0 0 0 5 4.77a5.44 5.44 0 0 0-1.5 3.78c0 5.42 3.3 6.61 6.44 7A3.37 3.37 0 0 0 9 18.13V22"></path></svg>
        View on GitHub
    </a>
</div>`
    },
    {
        title: "Project Directory",
        image: "/static/images/CarouselPreview3.jpg",
        content: `
            <h3>Project Directory</h3>
            <p class="mb-4">A comprehensive overview of all my projects.</p>

            <div class="project-list">
    <div style="background: rgba(255,255,255,0.05); border-radius: 8px; padding: 1.5rem; margin-bottom: 1rem; transition: all 0.3s ease;">
        <h4 style="color: #64ffda; margin-bottom: 0.5rem;">Portfolio Website</h4>
        <p style="color: #a8b2d1;">An interactive personal portfolio with underwater theme, demonstrating how AI assistance can help create production-ready websites from scratch. Features particle animations, dynamic content loading, and responsive design.</p>
        <div style="display: flex; gap: 1rem; margin-top: 1rem;">
            <a href="https://github.com/Aghbuul/Portfolio-Website" target="_blank" style="display: inline-flex; align-items: center; gap: 0.5rem; padding: 0.5rem 1rem; border-radius: 4px; background: rgba(100, 255, 218, 0.1); color: #64ffda; text-decoration: none; font-size: 0.9rem; border: 1px solid #64ffda; transition: all 0.2s ease-in-out;" onmouseover="this.style.background='rgba(100, 255, 218, 0.2)'; this.style.transform='scale(1.05)'" onmouseout="this.style.background='rgba(100, 255, 218, 0.1)'; this.style.transform='scale(1)'">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 19c-5 1.5-5-2.5-7-3m14 6v-3.87a3.37 3.37 0 0 0-.94-2.61c3.14-.35 6.44-1.54 6.44-7A5.44 5.44 0 0 0 20 4.77 5.07 5.07 0 0 0 19.91 1S18.73.65 16 2.48a13.38 13.38 0 0 0-7 0C6.27.65 5.09 1 5.09 1A5.07 5.07 0 0 0 5 4.77a5.44 5.44 0 0 0-1.5 3.78c0 5.42 3.3 6.61 6.44 7A3.37 3.37 0 0 0 9 18.13V22"></path></svg>
                GitHub
            </a>
        </div>
    </div>

    <div style="background: rgba(255,255,255,0.05); border-radius: 8px; padding: 1.5rem; margin-bottom: 1rem; transition: all 0.3s ease;">
        <h4 style="color: #64ffda; margin-bottom: 0.5rem;">SEIR Disease Modelling App</h4>
        <p style="color: #a8b2d1;">Interactive R Shiny application for epidemiological modelling, featuring real-time parameter adjustments, multiple scenario comparisons, and data export capabilities.</p>
        <div style="display: flex; gap: 1rem; margin-top: 1rem;">
            <a href="https://github.com/Aghbuul/interactive-seir-app" target="_blank" style="display: inline-flex; align-items: center; gap: 0.5rem; padding: 0.5rem 1rem; border-radius: 4px; background: rgba(100, 255, 218, 0.1); color: #64ffda; text-decoration: none; font-size: 0.9rem; border: 1px solid #64ffda; transition: all 0.2s ease-in-out;" onmouseover="this.style.background='rgba(100, 255, 218, 0.2)'; this.style.transform='scale(1.05)'" onmouseout="this.style.background='rgba(100, 255, 218, 0.1)'; this.style.transform='scale(1)'">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 19c-5 1.5-5-2.5-7-3m14 6v-3.87a3.37 3.37 0 0 0-.94-2.61c3.14-.35 6.44-1.54 6.44-7A5.44 5.44 0 0 0 20 4.77 5.07 5.07 0 0 0 19.91 1S18.73.65 16 2.48a13.38 13.38 0 0 0-7 0C6.27.65 5.09 1 5.09 1A5.07 5.07 0 0 0 5 4.77a5.44 5.44 0 0 0-1.5 3.78c0 5.42 3.3 6.61 6.44 7A3.37 3.37 0 0 0 9 18.13V22"></path></svg>
                GitHub
            </a>
        </div>
    </div>

    <div style="background: rgba(255,255,255,0.05); border-radius: 8px; padding: 1.5rem; margin-bottom: 1rem; transition: all 0.3s ease;">
        <h4 style="color: #64ffda; margin-bottom: 0.5rem;">Pixel Art Generator</h4>
        <p style="color: #a8b2d1;">Web-based tool for creating pixel art animations and sprite sheets. Features real-time image processing, animation creation, and video export capabilities using pure JavaScript and HTML5 Canvas.</p>
        <div style="display: flex; gap: 1rem; margin-top: 1rem;">
            <a href="https://pixel-art-generator.replit.app" target="_blank" style="display: inline-flex; align-items: center; gap: 0.5rem; padding: 0.5rem 1rem; border-radius: 4px; background: rgba(100, 255, 218, 0.1); color: #64ffda; text-decoration: none; font-size: 0.9rem; border: 1px solid #64ffda; transition: all 0.2s ease-in-out;" onmouseover="this.style.background='rgba(100, 255, 218, 0.2)'; this.style.transform='scale(1.05)'" onmouseout="this.style.background='rgba(100, 255, 218, 0.1)'; this.style.transform='scale(1)'">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h7"></path><line x1="16" y1="5" x2="22" y2="5"></line><line x1="22" y1="5" x2="22" y2="11"></line><line x1="16" y1="5" x2="22" y2="11"></line></svg>
                Try Now
            </a>
            <a href="https://github.com/Aghbuul/pixelcraft-studio" target="_blank" style="display: inline-flex; align-items: center; gap: 0.5rem; padding: 0.5rem 1rem; border-radius: 4px; background: rgba(100, 255, 218, 0.1); color: #64ffda; text-decoration: none; font-size: 0.9rem; border: 1px solid #64ffda; transition: all 0.2s ease-in-out;" onmouseover="this.style.background='rgba(100, 255, 218, 0.2)'; this.style.transform='scale(1.05)'" onmouseout="this.style.background='rgba(100, 255, 218, 0.1)'; this.style.transform='scale(1)'">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 19c-5 1.5-5-2.5-7-3m14 6v-3.87a3.37 3.37 0 0 0-.94-2.61c3.14-.35 6.44-1.54 6.44-7A5.44 5.44 0 0 0 20 4.77 5.07 5.07 0 0 0 19.91 1S18.73.65 16 2.48a13.38 13.38 0 0 0-7 0C6.27.65 5.09 1 5.09 1A5.07 5.07 0 0 0 5 4.77a5.44 5.44 0 0 0-1.5 3.78c0 5.42 3.3 6.61 6.44 7A3.37 3.37 0 0 0 9 18.13V22"></path></svg>
                GitHub
            </a>
        </div>
    </div>

    <div style="background: rgba(255,255,255,0.05); border-radius: 8px; padding: 1.5rem; margin-bottom: 1rem; transition: all 0.3s ease;">
        <h4 style="color: #64ffda; margin-bottom: 0.5rem;">Anime Sigil Eyes</h4>
        <p style="color: #a8b2d1;">ML-powered web application that detects facial features and overlays customisable anime-style sigils onto eyes, with real-time adjustments and export capabilities.</p>
        <div style="display: flex; gap: 1rem; margin-top: 1rem;">
            <a href="https://anime-eyes.replit.app" target="_blank" style="display: inline-flex; align-items: center; gap: 0.5rem; padding: 0.5rem 1rem; border-radius: 4px; background: rgba(100, 255, 218, 0.1); color: #64ffda; text-decoration: none; font-size: 0.9rem; border: 1px solid #64ffda; transition: all 0.2s ease-in-out;" onmouseover="this.style.background='rgba(100, 255, 218, 0.2)'; this.style.transform='scale(1.05)'" onmouseout="this.style.background='rgba(100, 255, 218, 0.1)'; this.style.transform='scale(1)'">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h7"></path><line x1="16" y1="5" x2="22" y2="5"></line><line x1="22" y1="5" x2="22" y2="11"></line><line x1="16" y1="5" x2="22" y2="11"></line></svg>
                Try Now
            </a>
            <a href="https://github.com/Aghbuul/Anime-Sigil-Eyes" target="_blank" style="display: inline-flex; align-items: center; gap: 0.5rem; padding: 0.5rem 1rem; border-radius: 4px; background: rgba(100, 255, 218, 0.1); color: #64ffda; text-decoration: none; font-size: 0.9rem; border: 1px solid #64ffda; transition: all 0.2s ease-in-out;" onmouseover="this.style.background='rgba(100, 255, 218, 0.2)'; this.style.transform='scale(1.05)'" onmouseout="this.style.background='rgba(100, 255, 218, 0.1)'; this.style.transform='scale(1)'">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 19c-5 1.5-5-2.5-7-3m14 6v-3.87a3.37 3.37 0 0 0-.94-2.61c3.14-.35 6.44-1.54 6.44-7A5.44 5.44 0 0 0 20 4.77 5.07 5.07 0 0 0 19.91 1S18.73.65 16 2.48a13.38 13.38 0 0 0-7 0C6.27.65 5.09 1 5.09 1A5.07 5.07 0 0 0 5 4.77a5.44 5.44 0 0 0-1.5 3.78c0 5.42 3.3 6.61 6.44 7A3.37 3.37 0 0 0 9 18.13V22"></path></svg>
                GitHub
            </a>
        </div>
    </div>

    <div style="background: rgba(255,255,255,0.05); border-radius: 8px; padding: 1.5rem; margin-bottom: 1rem; transition: all 0.3s ease;">
        <h4 style="color: #64ffda; margin-bottom: 0.5rem;">SEIR Model Templates</h4>
        <p style="color: #a8b2d1;">Collection of ready-to-use SEIR model templates in R, designed for quick implementation in epidemiological research and analysis.</p>
        <div style="display: flex; gap: 1rem; margin-top: 1rem;">
            <a href="https://github.com/Aghbuul/SEIR-Model-Templates" target="_blank" style="display: inline-flex; align-items: center; gap: 0.5rem; padding: 0.5rem 1rem; border-radius: 4px; background: rgba(100, 255, 218, 0.1); color: #64ffda; text-decoration: none; font-size: 0.9rem; border: 1px solid #64ffda; transition: all 0.2s ease-in-out;" onmouseover="this.style.background='rgba(100, 255, 218, 0.2)'; this.style.transform='scale(1.05)'" onmouseout="this.style.background='rgba(100, 255, 218, 0.1)'; this.style.transform='scale(1)'">
   <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 19c-5 1.5-5-2.5-7-3m14 6v-3.87a3.37 3.37 0 0 0-.94-2.61c3.14-.35 6.44-1.54 6.44-7A5.44 5.44 0 0 0 20 4.77 5.07 5.07 0 0 0 19.91 1S18.73.65 16 2.48a13.38 13.38 0 0 0-7 0C6.27.65 5.09 1 5.09 1A5.07 5.07 0 0 0 5 4.77a5.44 5.44 0 0 0-1.5 3.78c0 5.42 3.3 6.61 6.44 7A3.37 3.37 0 0 0 9 18.13V22"></path></svg>
   GitHub
</a>
           </div>
       </div>
   </div>

   <div style="margin-top: 2rem; padding-top: 1rem; border-top: 1px solid rgba(255,255,255,0.1);">
       <a href="https://github.com/Aghbuul" target="_blank" style="color: #64ffda; text-decoration: none; display: flex; align-items: center; justify-content: center; gap: 0.5rem;">
           <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 19c-5 1.5-5-2.5-7-3m14 6v-3.87a3.37 3.37 0 0 0-.94-2.61c3.14-.35 6.44-1.54 6.44-7A5.44 5.44 0 0 0 20 4.77 5.07 5.07 0 0 0 19.91 1S18.73.65 16 2.48a13.38 13.38 0 0 0-7 0C6.27.65 5.09 1 5.09 1A5.07 5.07 0 0 0 5 4.77a5.44 5.44 0 0 0-1.5 3.78c0 5.42 3.3 6.61 6.44 7A3.37 3.37 0 0 0 9 18.13V22"></path></svg>
           View Full Profile on GitHub
       </a>
   </div>`
        }
];

    function showProjectDetails(index) {
        const project = projectDetails[index];
        const modal = document.getElementById('projectModal');

        // Set modal content
        modal.querySelector('.modal-title').textContent = project.title;
        modal.querySelector('.project-detail-image').innerHTML = `
            <div class="modal-header-image" style="
                height: 250px;
                background: linear-gradient(0deg, 
                    rgba(0, 24, 48, 0.9) 0%,
                    rgba(0, 51, 102, 0.5) 50%,
                    rgba(0, 153, 255, 0.3) 100%
                ),
                url('${project.image}');
                background-size: cover;
                background-position: top;
                border-radius: 8px;
            "></div>`;
        
    modal.querySelector('.project-detail-content').innerHTML = project.content;

    // Show modal
    const modalInstance = new bootstrap.Modal(modal, {
        backdrop: true,    // Allows closing on background click
        keyboard: true     // Allows closing with Esc key
    });

    // Store the scroll position
    const scrollPosition = window.scrollY;

    // Add custom class to body when modal opens
    modal.addEventListener('shown.bs.modal', function () {
        document.body.style.top = `-${scrollPosition}px`;
        document.body.classList.add('modal-open');
        document.body.style.position = 'fixed';
        document.body.style.width = '100%';
        // Pause carousel
        const carousel = document.getElementById('projectCarousel');
        const carouselInstance = bootstrap.Carousel.getInstance(carousel);
        if (carouselInstance) {
            carouselInstance.pause();
        }
    });

    // Restore scroll position when modal closes
    modal.addEventListener('hidden.bs.modal', function () {
        document.body.style.position = '';
        document.body.style.top = '';
        document.body.style.width = '';
        document.body.classList.remove('modal-open');
        window.scrollTo(0, scrollPosition);
        // Resume carousel
        const carousel = document.getElementById('projectCarousel');
        const carouselInstance = bootstrap.Carousel.getInstance(carousel);
        if (carouselInstance) {
            carouselInstance.cycle();
        }
    });

    modalInstance.show();
}