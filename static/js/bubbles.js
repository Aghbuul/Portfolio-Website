class Bubble {
    constructor(x, y) {
        this.size = Math.random() * 2 + 2;
        this.x = x;
        this.y = y;
        this.speedY = Math.random() * 3 + 1.5;
        this.speedX = 0;
        this.opacity = Math.random() * 0.5 + 0.1;
        // Only ~20% of bubbles will have a lifetime
        this.hasLifetime = Math.random() < 0.2;
        this.lifetime = 0;
        this.maxLifetime = Math.random() * 300 + 100; // Random lifetime between 1.6-6.6 seconds
    }

  update(mouseX, mouseY) {
      this.lifetime++;
      if (this.lifetime >= this.maxLifetime) {
          return false; // Bubble should be removed
      }

      this.y -= this.speedY;

      const dx = mouseX - this.x;
      const dy = mouseY - this.y;
      const distance = Math.sqrt(dx * dx + dy * dy);

      if (distance < 150) {
          const angle = Math.atan2(dy, dx);
          this.speedX = -Math.cos(angle) * (150 - distance) / 50;
      } else {
          this.speedX *= 0.95;
      }

      this.x += this.speedX;
      return true; // Bubble stays alive
  }

  // Draw method remains the same
}

function initBubbles() {
  const canvas = document.createElement('canvas');
  canvas.style.position = 'fixed';
  canvas.style.top = '0';
  canvas.style.left = '0';
  canvas.style.pointerEvents = 'none';
  canvas.style.zIndex = '1';

  document.body.appendChild(canvas);

  const ctx = canvas.getContext('2d');
  let bubbles = [];
  let mousePos = { x: 0, y: 0 };

  function handleResize() {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
  }

  handleResize();
  window.addEventListener('resize', handleResize);

    function createBurst() {
        // Always spawn from bottom
        for (let i = 0; i < 100; i++) { // Increased number of bubbles per burst
            const x = Math.random() * canvas.width; // Random position along bottom
            const y = canvas.height + Math.random() * 20; // Slightly below screen
            bubbles.push(new Bubble(x, y));
        }
    }

  function animate() {
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      // Update and filter out dead bubbles
      bubbles = bubbles.filter(bubble => bubble.update(mousePos.x, mousePos.y));

      // Draw remaining bubbles
      bubbles.forEach(bubble => bubble.draw(ctx));

      requestAnimationFrame(animate);
  }

  document.addEventListener('mousemove', (e) => {
      mousePos = { x: e.clientX, y: e.clientY };
  });

  // Create initial burst
  createBurst();

  // Create new bursts every 20 seconds
    setInterval(() => {
        // Create multiple bursts over 2 seconds
        let burstCount = 0;
        const burstInterval = setInterval(() => {
            createBurst();
            burstCount++;
            if (burstCount >= 4) { // 4 bursts over 2 seconds
                clearInterval(burstInterval);
            }
        }, 500); // Every 0.5 seconds
    }, 20000); // Every 20 secondsInterval(createBurst, 20000);

  animate();
}

// Initialize when the page loads
document.addEventListener('DOMContentLoaded', initBubbles);