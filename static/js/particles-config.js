// Configure the background particles for all sections
function configureParticles(containerId, isBelowTop = false) {
    // Unified configuration for all sections with smooth interactions
    const config = {
        particles: {
            number: {
                value: isBelowTop ? 50 : 80,
                density: { enable: true, value_area: 800 }
            },
            color: { 
                value: isBelowTop ? 
                    ['#1b3b5f', '#275d85', '#00aaff', '#ffffff'] : 
                    ['#ffffff', '#e0f7ff', '#b3ecff']
            },
            shape: {
                type: 'circle',
                stroke: { width: 1, color: 'rgba(255,255,255,0.3)' }
            },
            opacity: {
                value: isBelowTop ? 0.6 : 0.8,
                random: true,
                anim: {
                    enable: true,
                    speed: 0.3,
                    opacity_min: 0.2,
                    sync: false
                }
            },
            size: {
                value: isBelowTop ? 2 : 4,
                random: true,
                anim: {
                    enable: true,
                    speed: 2,
                    size_min: 2,
                    sync: false
                }
            },
            line_linked: {
                enable: false
            },
            move: {
                enable: true,
                speed: isBelowTop ? 2 : 1.5,
                direction: 'top',
                random: true,
                straight: false,
                out_mode: 'out',
                bounce: false,
                attract: {
                    enable: true,
                    rotateX: 300,
                    rotateY: 600
                }
            }
        },
        interactivity: {
            detect_on: 'canvas',
            events: {
                onhover: {
                    enable: true,
                    mode: 'grab'
                },
                onclick: {
                    enable: true,
                    mode: 'push'
                },
                resize: true
            },
            modes: {
                grab: {
                    distance: 80,
                    line_linked: {
                        opacity: 0.5 // Line transparency
                    }
                },
                push: {
                    particles_nb: isBelowTop ? 2 : 4
                }
            }
        },
        retina_detect: true
    };

    // Initialize particles with this configuration
    particlesJS(containerId, config);
}

// Initialize particles for each section
// Hero section - special configuration with repulsion and click effects
configureParticles('particles-js', false);  // Use the interactive configuration for hero

// Content sections - standard configuration
configureParticles('education-particles', true);    // Education section
configureParticles('skills-particles', true);       // Skills section
configureParticles('ai-tools-particles', true);     // AI Tools section
configureParticles('experience-particles', true);    // Work Experience section
configureParticles('projects-particles', true);      // Projects section
configureParticles('awards-particles', true);        // Awards section
configureParticles('cv-particles', true);           // CV section