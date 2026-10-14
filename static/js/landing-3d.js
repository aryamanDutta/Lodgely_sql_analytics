/**
 * Lodgely — Interactive 3D Scroll-Driven Architectural Background
 * 
 * Features:
 * - Procedural luxury architectural hotel sculpture (plinth, pavilions, archways, colonnade, glowing portal)
 * - Lavender, violet, and warm peach/orange materials matching Lodgely palette
 * - Silky smooth scroll-driven rotation, parallax, and depth shifts with lerp dampening
 * - Respects prefers-reduced-motion
 * - WebGL availability detection with graceful fallback
 * - Tab visibility detection (pauses RAF when hidden)
 * - Capped DPR and optimized geometry reuse for student laptop performance
 * - Independent non-intercepting background layer (pointer-events: none)
 */

(function () {
  'use strict';

  // Check WebGL availability
  function isWebGLAvailable() {
    try {
      const canvas = document.createElement('canvas');
      return !!(window.WebGLRenderingContext && (canvas.getContext('webgl') || canvas.getContext('experimental-webgl')));
    } catch (e) {
      return false;
    }
  }

  if (!isWebGLAvailable() || typeof THREE === 'undefined') {
    return;
  }

  // Check prefers-reduced-motion
  const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  // DOM Canvas
  const canvas = document.getElementById('landing-3d-canvas');
  if (!canvas) return;

  // Scene setup
  const scene = new THREE.Scene();
  scene.fog = new THREE.FogExp2(0xF4F2F8, 0.04);

  // Camera
  const camera = new THREE.PerspectiveCamera(42, window.innerWidth / window.innerHeight, 0.1, 100);
  camera.position.set(0, 0, 11);

  // Renderer
  const renderer = new THREE.WebGLRenderer({
    canvas: canvas,
    antialias: true,
    alpha: true,
    powerPreference: 'high-performance'
  });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 1.75));
  renderer.setSize(window.innerWidth, window.innerHeight);
  renderer.setClearColor(0xF4F2F8, 0); // Transparent so CSS gradients shine through

  // ---------------------------------------------------------------------------
  // LIGHTING
  // ---------------------------------------------------------------------------
  const ambientLight = new THREE.AmbientLight(0xF7F4FF, 0.95);
  scene.add(ambientLight);

  // Warm peach key light (representing golden morning/evening light)
  const keyLight = new THREE.DirectionalLight(0xFFE2D0, 1.35);
  keyLight.position.set(5, 7, 6);
  scene.add(keyLight);

  // Lavender fill light from the left
  const fillLight = new THREE.DirectionalLight(0xD8CCFA, 0.85);
  fillLight.position.set(-6, -2, 4);
  scene.add(fillLight);

  // Top soft violet rim light
  const rimLight = new THREE.DirectionalLight(0xEAE2FD, 0.6);
  rimLight.position.set(0, 6, -5);
  scene.add(rimLight);

  // Warm glowing doorway portal light
  const portalLight = new THREE.PointLight(0xFFA872, 1.8, 5.5);
  portalLight.position.set(0, -0.6, 1.0);
  scene.add(portalLight);

  // ---------------------------------------------------------------------------
  // MATERIALS (Lavender, Violet, Peach, and Frosted Glass)
  // ---------------------------------------------------------------------------
  const matWhitePlinth = new THREE.MeshStandardMaterial({
    color: 0xFDFBFF,
    roughness: 0.25,
    metalness: 0.05
  });

  const matLavenderPlinth = new THREE.MeshStandardMaterial({
    color: 0xDDD4F8,
    roughness: 0.35,
    metalness: 0.08
  });

  const matPeachAccent = new THREE.MeshStandardMaterial({
    color: 0xFFA872,
    roughness: 0.2,
    metalness: 0.45
  });

  const matFrostedGlass = new THREE.MeshStandardMaterial({
    color: 0xEEE8FB,
    roughness: 0.18,
    metalness: 0.12,
    transparent: true,
    opacity: 0.82
  });

  const matVioletWing = new THREE.MeshStandardMaterial({
    color: 0xD3C6F7,
    roughness: 0.28,
    metalness: 0.05,
    transparent: true,
    opacity: 0.9
  });

  const matGoldTrim = new THREE.MeshStandardMaterial({
    color: 0xF8B688,
    roughness: 0.15,
    metalness: 0.75
  });

  const matColumn = new THREE.MeshStandardMaterial({
    color: 0xFFFFFF,
    roughness: 0.15,
    metalness: 0.05
  });

  const matGlowingPortal = new THREE.MeshStandardMaterial({
    color: 0xFF762F,
    emissive: 0xFFA066,
    emissiveIntensity: 0.9,
    roughness: 0.2
  });

  // Track all materials for opacity fading near footer
  const fadeMaterials = [
    matWhitePlinth, matLavenderPlinth, matPeachAccent, matFrostedGlass,
    matVioletWing, matGoldTrim, matColumn, matGlowingPortal
  ];

  // ---------------------------------------------------------------------------
  // ARCHITECTURAL HOTEL SCULPTURE ASSEMBLY
  // ---------------------------------------------------------------------------
  const hotelSculpture = new THREE.Group();

  // 1. Terraced Podium Plinth
  const tier1Geo = new THREE.CylinderGeometry(4.0, 4.3, 0.4, 48);
  const tier1Mesh = new THREE.Mesh(tier1Geo, matWhitePlinth);
  tier1Mesh.position.y = -2.2;
  hotelSculpture.add(tier1Mesh);

  const tier2Geo = new THREE.CylinderGeometry(3.4, 3.65, 0.35, 48);
  const tier2Mesh = new THREE.Mesh(tier2Geo, matLavenderPlinth);
  tier2Mesh.position.y = -1.85;
  hotelSculpture.add(tier2Mesh);

  const plinthRingGeo = new THREE.TorusGeometry(3.55, 0.045, 16, 64);
  const plinthRing = new THREE.Mesh(plinthRingGeo, matPeachAccent);
  plinthRing.rotation.x = Math.PI / 2;
  plinthRing.position.y = -1.68;
  hotelSculpture.add(plinthRing);

  // 2. Main Center Tower Pavilion (Sleek, rounded modern hotel wing)
  const mainTowerGeo = new THREE.BoxGeometry(2.2, 4.0, 1.8);
  const mainTower = new THREE.Mesh(mainTowerGeo, matFrostedGlass);
  mainTower.position.set(0, 0.45, -0.3);
  hotelSculpture.add(mainTower);

  // Modern horizontal band / floor divisions on the main tower
  for (let i = -1; i <= 2; i++) {
    const bandGeo = new THREE.BoxGeometry(2.26, 0.06, 1.86);
    const bandMesh = new THREE.Mesh(bandGeo, matPeachAccent);
    bandMesh.position.set(0, i * 0.9, -0.3);
    hotelSculpture.add(bandMesh);
  }

  // 3. West Pavilion Wing (Interlocking stepped volume)
  const westWingGeo = new THREE.BoxGeometry(1.6, 2.7, 1.5);
  const westWing = new THREE.Mesh(westWingGeo, matVioletWing);
  westWing.position.set(-1.8, -0.25, 0.1);
  hotelSculpture.add(westWing);

  // West Wing roof terrace canopy
  const westCanopyGeo = new THREE.BoxGeometry(1.75, 0.1, 1.65);
  const westCanopy = new THREE.Mesh(westCanopyGeo, matGoldTrim);
  westCanopy.position.set(-1.8, 1.15, 0.1);
  hotelSculpture.add(westCanopy);

  // 4. East Cantilever Balcony / Lounge Wing
  const eastWingGeo = new THREE.BoxGeometry(1.5, 0.25, 2.4);
  const eastWing = new THREE.Mesh(eastWingGeo, matWhitePlinth);
  eastWing.position.set(1.4, 0.6, 0.3);
  hotelSculpture.add(eastWing);

  const eastSupportGeo = new THREE.CylinderGeometry(0.07, 0.07, 2.2, 16);
  const eastSupport1 = new THREE.Mesh(eastSupportGeo, matColumn);
  eastSupport1.position.set(1.9, -0.55, 1.2);
  hotelSculpture.add(eastSupport1);

  const eastSupport2 = new THREE.Mesh(eastSupportGeo, matColumn);
  eastSupport2.position.set(1.9, -0.55, -0.6);
  hotelSculpture.add(eastSupport2);

  // 5. Layered Grand Entrance Archways & Colonnade
  function createArch(radius, height, zPos, material) {
    const archGroup = new THREE.Group();

    // Semi-torus archway crown
    const crownGeo = new THREE.TorusGeometry(radius, 0.08, 16, 32, Math.PI);
    const crown = new THREE.Mesh(crownGeo, material);
    crown.position.y = height;
    archGroup.add(crown);

    // Left and right pillars
    const pillarGeo = new THREE.CylinderGeometry(0.08, 0.08, height + 1.6, 16);
    const leftPillar = new THREE.Mesh(pillarGeo, material);
    leftPillar.position.set(-radius, (height - 1.6) / 2, 0);
    archGroup.add(leftPillar);

    const rightPillar = new THREE.Mesh(pillarGeo, material);
    rightPillar.position.set(radius, (height - 1.6) / 2, 0);
    archGroup.add(rightPillar);

    archGroup.position.z = zPos;
    return archGroup;
  }

  // 3 Concentric Layered Archways
  const outerArch = createArch(1.15, 1.4, 0.8, matWhitePlinth);
  const middleArch = createArch(0.92, 1.15, 1.05, matLavenderPlinth);
  const innerArch = createArch(0.68, 0.95, 1.3, matPeachAccent);
  hotelSculpture.add(outerArch);
  hotelSculpture.add(middleArch);
  hotelSculpture.add(innerArch);

  // 6. Fluted Architectural Colonnade (Terrace facade columns)
  const columnPositions = [-1.3, -0.7, 0.7, 1.3];
  columnPositions.forEach(x => {
    const colGeo = new THREE.CylinderGeometry(0.06, 0.06, 1.9, 16);
    const colMesh = new THREE.Mesh(colGeo, matColumn);
    colMesh.position.set(x, -0.75, 1.55);
    hotelSculpture.add(colMesh);
  });

  // 7. Inner Glowing Sanctuary / Doorway
  const portalGeo = new THREE.BoxGeometry(0.72, 1.35, 0.12);
  const portalMesh = new THREE.Mesh(portalGeo, matGlowingPortal);
  portalMesh.position.set(0, -0.85, 0.58);
  hotelSculpture.add(portalMesh);

  // 8. Delicate Floating Luxury Halo Ring
  const haloGeo = new THREE.TorusGeometry(1.8, 0.035, 16, 64);
  const haloRing = new THREE.Mesh(haloGeo, matGoldTrim);
  haloRing.position.set(0, 2.7, -0.2);
  haloRing.rotation.x = Math.PI / 3.2;
  haloRing.rotation.y = Math.PI / 7;
  hotelSculpture.add(haloRing);

  scene.add(hotelSculpture);

  // ---------------------------------------------------------------------------
  // AMBIENT ATMOSPHERIC MOTES / PARTICLES (Subtle luxury air dust)
  // ---------------------------------------------------------------------------
  const moteCount = 75;
  const moteGeo = new THREE.BufferGeometry();
  const motePositions = new Float32Array(moteCount * 3);

  for (let i = 0; i < moteCount; i++) {
    motePositions[i * 3] = (Math.random() - 0.5) * 16;
    motePositions[i * 3 + 1] = (Math.random() - 0.5) * 12;
    motePositions[i * 3 + 2] = (Math.random() - 0.5) * 10;
  }
  moteGeo.setAttribute('position', new THREE.BufferAttribute(motePositions, 3));

  const moteMat = new THREE.PointsMaterial({
    color: 0xCBBDF4,
    size: 0.07,
    transparent: true,
    opacity: 0.65
  });
  const motePoints = new THREE.Points(moteGeo, moteMat);
  scene.add(motePoints);

  // ---------------------------------------------------------------------------
  // RESPONSIVE SCALING & CAMERA
  // ---------------------------------------------------------------------------
  function updateLayout() {
    const width = window.innerWidth;
    const height = window.innerHeight;

    camera.aspect = width / height;
    camera.updateProjectionMatrix();
    renderer.setSize(width, height);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 1.75));

    // On narrow screens (mobile/tablet), adjust scale and position
    if (width < 768) {
      hotelSculpture.scale.set(0.68, 0.68, 0.68);
    } else if (width < 1200) {
      hotelSculpture.scale.set(0.85, 0.85, 0.85);
    } else {
      hotelSculpture.scale.set(1.0, 1.0, 1.0);
    }
  }
  updateLayout();
  window.addEventListener('resize', updateLayout, { passive: true });

  // ---------------------------------------------------------------------------
  // INTERACTIVE CURSOR PARALLAX (Subtle micro-reaction)
  // ---------------------------------------------------------------------------
  let targetMouseX = 0;
  let targetMouseY = 0;
  let currentMouseX = 0;
  let currentMouseY = 0;

  if (!prefersReducedMotion) {
    window.addEventListener('mousemove', e => {
      targetMouseX = (e.clientX / window.innerWidth - 0.5) * 0.4;
      targetMouseY = (e.clientY / window.innerHeight - 0.5) * 0.3;
    }, { passive: true });
  }

  // ---------------------------------------------------------------------------
  // SCROLL-DRIVEN TIMELINE & INTERPOLATION
  // ---------------------------------------------------------------------------
  let targetScrollProgress = 0;
  let currentScrollProgress = 0;

  function onScroll() {
    const maxScroll = Math.max(document.documentElement.scrollHeight - window.innerHeight, 1);
    targetScrollProgress = Math.min(Math.max(window.scrollY / maxScroll, 0), 1);
  }
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll(); // initial measurement

  // Linear interpolation helper
  function lerp(start, end, factor) {
    return start + (end - start) * factor;
  }

  // Visibility / Tab switching optimization
  let isTabActive = true;
  document.addEventListener('visibilitychange', () => {
    isTabActive = !document.hidden;
  });

  // ---------------------------------------------------------------------------
  // ANIMATION RENDER LOOP
  // ---------------------------------------------------------------------------
  let clock = new THREE.Clock();

  function animate() {
    requestAnimationFrame(animate);

    if (!isTabActive) return;

    const elapsedTime = clock.getElapsedTime();

    if (prefersReducedMotion) {
      // Static, composed, tranquil architectural angle
      const isMobile = window.innerWidth < 768;
      hotelSculpture.position.set(isMobile ? 0 : 2.2, -0.3, -0.5);
      hotelSculpture.rotation.set(0.18, -0.38, 0.04);
      renderer.render(scene, camera);
      return;
    }

    // 1. Smooth lerp for scroll progress & cursor
    currentScrollProgress += (targetScrollProgress - currentScrollProgress) * 0.055;
    currentMouseX += (targetMouseX - currentMouseX) * 0.04;
    currentMouseY += (targetMouseY - currentMouseY) * 0.04;

    const p = currentScrollProgress;
    const isMobile = window.innerWidth < 768;

    // 2. Timeline Coordinates according to Section
    // Hero: p = 0 -> floats to right (desktop) or centered behind (mobile)
    // Dashboard: p = 0.25 -> moves center-back, subtle depth behind dashboard preview
    // Features: p = 0.6 -> pivots to profile, drifts left
    // CTA & Footer: p = 0.9+ -> descends and fades out
    let posX, posY, posZ;
    let rotX, rotY, rotZ;
    let globalOpacity = 1.0;

    if (p <= 0.28) {
      // Stage 1: Hero Section
      const t = p / 0.28;
      const startX = isMobile ? 0 : 2.4;
      const endX = isMobile ? 0 : 0.4;
      posX = lerp(startX, endX, t);
      posY = lerp(-0.2, 0.4, t);
      posZ = lerp(-0.4, -2.2, t);

      rotX = lerp(0.14, 0.22, t);
      rotY = lerp(-0.48, 0.25, t);
      rotZ = lerp(0.04, -0.06, t);
    } else if (p <= 0.68) {
      // Stage 2: Dashboard Preview & First Capability Features
      const t = (p - 0.28) / (0.68 - 0.28);
      const startX = isMobile ? 0 : 0.4;
      const endX = isMobile ? 0 : -2.3;
      posX = lerp(startX, endX, t);
      posY = lerp(0.4, -0.6, t);
      posZ = lerp(-2.2, -1.6, t);

      rotX = lerp(0.22, 0.16, t);
      rotY = lerp(0.25, 1.15, t);
      rotZ = lerp(-0.06, 0.08, t);
    } else {
      // Stage 3: Core Operations, Analytics, and Final CTA Dissolve
      const t = (p - 0.68) / (1.0 - 0.68);
      const startX = isMobile ? 0 : -2.3;
      const endX = isMobile ? 0 : -1.0;
      posX = lerp(startX, endX, t);
      posY = lerp(-0.6, -3.8, t);
      posZ = lerp(-1.6, -4.5, t);

      rotX = lerp(0.16, 0.1, t);
      rotY = lerp(1.15, 1.8, t);
      rotZ = lerp(0.08, 0.02, t);

      // Dissolve gently near the CTA banner and footer
      if (p > 0.82) {
        globalOpacity = Math.max(1.0 - (p - 0.82) / 0.14, 0.0);
      }
    }

    // Gentle micro-floating oscillation
    const floatY = Math.sin(elapsedTime * 1.1) * 0.07;
    const floatRotY = Math.cos(elapsedTime * 0.85) * 0.025;

    // Apply computed transforms + cursor parallax
    hotelSculpture.position.x = posX + currentMouseX;
    hotelSculpture.position.y = posY + floatY - currentMouseY;
    hotelSculpture.position.z = posZ;

    hotelSculpture.rotation.x = rotX - currentMouseY * 0.2;
    hotelSculpture.rotation.y = rotY + floatRotY + currentMouseX * 0.3;
    hotelSculpture.rotation.z = rotZ;

    // Slowly spin the luxury floating halo
    haloRing.rotation.z = elapsedTime * 0.3;

    // Pulsing warm glow from doorway portal
    portalLight.intensity = 1.6 + Math.sin(elapsedTime * 2.2) * 0.35;

    // Atmospheric motes slow drift
    motePoints.rotation.y = elapsedTime * 0.025;
    motePoints.rotation.x = elapsedTime * 0.015;

    // Update material opacity for gentle fade near CTA
    fadeMaterials.forEach(mat => {
      mat.opacity = (mat === matFrostedGlass ? 0.82 : 1.0) * globalOpacity;
      mat.transparent = true;
    });
    canvas.style.opacity = globalOpacity.toFixed(3);

    renderer.render(scene, camera);
  }

  // Start rendering
  animate();

})();
