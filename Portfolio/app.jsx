// Emilia Małecka · Portfolio · main app v3 (full-bleed, hot-spot signpost)

const { useState, useEffect, useRef, useMemo, useCallback } = React;

const TWEAK_DEFAULTS = /*EDITMODE-BEGIN*/{
  "headlineHomePL": "Eksploruj moje portfolio.",
  "headlineHomeEN": "Explore my portfolio.",
  "headlineMapPL": "Wybierz miejsce, rozpocznij podróż.",
  "headlineMapEN": "Pick a place, begin the journey.",
  "projectCount": 3,
  "ambient": true
}/*EDITMODE-END*/;

function splitHeadline(s) {
  if (!s) return ['', ''];
  const m = s.match(/^(\S+)\s+([\s\S]*)$/);
  return m ? [m[1], m[2]] : [s, ''];
}
function splitMapHeadline(s) {
  if (!s) return ['', ''];
  const i = s.indexOf(',');
  if (i < 0) return [s, ''];
  return [s.slice(0, i + 1), s.slice(i + 1).trim()];
}

/* ─── Burn Reveal: SVG turbulence filter + mask defs (hidden, 0×0) ─── */
function BurnRevealSVG() {
  return (
    <svg id="burn-svg"
      style={{position:'absolute',width:0,height:0,overflow:'hidden'}}
      aria-hidden="true">
      <defs>
        {/* Turbulence displaces the reveal circle edge → organic, parchment-like */}
        {/* Soft radial gradient fills the circle — edge fades before distortion smears it */}
        {/* Wider soft falloff → more of the edge is in the "dragging" zone */}
        <radialGradient id="burn-grad" cx="50%" cy="50%" r="50%">
          <stop offset="58%" stopColor="white" stopOpacity="1"/>
          <stop offset="78%" stopColor="white" stopOpacity="0.5"/>
          <stop offset="100%" stopColor="white" stopOpacity="0"/>
        </radialGradient>
        {/* Low-frequency, high-scale turbulence → big sweeping organic tendrils */}
        <filter id="burn-distort"
          x="-60%" y="-60%" width="220%" height="220%"
          colorInterpolationFilters="sRGB">
          <feTurbulence type="turbulence"
            baseFrequency="0.008 0.011"
            numOctaves="6" seed="9" result="noise"/>
          <feDisplacementMap
            in="SourceGraphic" in2="noise"
            scale="155"
            xChannelSelector="R" yChannelSelector="G"/>
        </filter>
        {/* The mask: expanding gradient circle with heavily distorted edges */}
        <mask id="burn-mask" maskUnits="userSpaceOnUse"
          x="0" y="0" width="5000" height="5000">
          <circle id="burn-circle" r="0"
            fill="url(#burn-grad)"
            filter="url(#burn-distort)"/>
        </mask>
      </defs>
    </svg>
  );
}

/* ─── kwiaty: prawa strona przy drogowskazie, dwie fazy animacji ─── */
function HomeKwiaty() {
  return (
    <div className="kwiaty-layer" aria-hidden="true">
      <div className="kwiat-wrap k1">
        <img src="assets/kwiaty.png?v=4" alt="" />
      </div>
      <div className="kwiat-wrap k2">
        <img src="assets/kwiaty.png?v=4" alt="" />
      </div>
      {/* kwiaty1 — dwie łodyżki, wyżej i bardziej w lewo */}
      <div className="kwiat-wrap k3">
        <img src="assets/kwiaty1.png?v=4" alt="" />
      </div>
      {/* kwiaty1 — przy drogowskazie, prawy dolny róg */}
      <div className="kwiat-wrap k4">
        <img src="assets/kwiaty1.png?v=4" alt="" />
      </div>
      {/* kwiaty-lewa1 — wysoki kwiat, lewa strona */}
      <div className="kwiat-wrap k5">
        <img src="assets/kwiaty-lewa1.png?v=4" alt="" />
      </div>
      {/* kwiaty-lewa2 — mniejszy kwiat, lekko z boku */}
      <div className="kwiat-wrap k6">
        <img src="assets/kwiaty-lewa2.png?v=4" alt="" />
      </div>
      {/* kwiaty-lewa2 — obok kwiata 1 */}
      <div className="kwiat-wrap k7">
        <img src="assets/kwiaty-lewa2.png?v=4" alt="" />
      </div>
      {/* kwiaty-lewa2 — dodatkowy, minimalnie większy */}
      <div className="kwiat-wrap k8">
        <img src="assets/kwiaty-lewa2.png?v=4" alt="" />
      </div>
      {/* kwiaty-lewa1 — mniejszy, na dole */}
      <div className="kwiat-wrap k9">
        <img src="assets/kwiaty-lewa1.png?v=4" alt="" />
      </div>
      {/* kwiaty-lewa2 — dodatkowy, bliżej lewej */}
      <div className="kwiat-wrap k10">
        <img src="assets/kwiaty-lewa2.png?v=4" alt="" />
      </div>
    </div>
  );
}

/* ─── ambient layer: birds only ─── */
function AmbientLayers({ ambient }) {
  const birds = useMemo(() => Array.from({ length: 2 }, (_, i) => ({
    top: 8 + i * 7,
    dur: 70 + Math.random() * 50,
    delay: -Math.random() * 90,
  })), []);
  if (!ambient) return null;
  return (
    <div className="amb" aria-hidden="true">
      {birds.map((b,i) => (
        <div key={'b'+i} className="bird" style={{
          top: b.top + '%',
          animationDuration: b.dur + 's',
          animationDelay: b.delay + 's',
          '--wdelay': (-Math.random() * 0.55).toFixed(2) + 's',
        }}/>
      ))}
    </div>
  );
}


/* ─── shared chrome (brand + lang switch) ─── */
function Chrome({ lang, setLang, onHome }) {
  return (
    <div className="chrome">
      <button className="brand" onClick={onHome} title="Home">
        <span className="brand-name">Emilia Małecka</span>
      </button>
      <div className="lang">
        <button className={lang === 'pl' ? 'on' : ''} onClick={() => setLang('pl')}>PL</button>
        <span className="dot">•</span>
        <button className={lang === 'en' ? 'on' : ''} onClick={() => setLang('en')}>EN</button>
      </div>
    </div>
  );
}

/* ─── Blink canvas: animowane powieki — wyłącznie wewnątrz soczewek okularów ─── */
function BlinkCanvas() {
  const canvasRef = React.useRef(null);

  React.useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');

    /* Obraz postaci: 1920×2443, object-fit:contain, object-position:58% 84%,
       transform: translateY(13%) scale(1.10)                                  */
    const IMG_W = 1920, IMG_H = 2443;
    const OBJ_X = 0.58, OBJ_Y = 0.84;
    const CSS_S = 1.10, CSS_TY = 0.13;

    /* Centra oczu w przestrzeni obrazu.
       Y skalibrowane wizualnie: fioletowe znaczniki na screenshocie
       wskazały że 466px (19.1%) było za nisko — właściwe to ~340px (13.9%).
       Promień soczewki wewnętrznej ~36px w przestrzeni obrazu.          */
    /* rot: lewe oko CW (+) → lewa strona w dół, prawa w górę
             prawe oko CCW (−) → lewa strona w górę, prawa w dół   */
    const EYES = [
      { ix: 828 / IMG_W, iy: 376 / IMG_H, rot:  0.18 },
      { ix: 947 / IMG_W, iy: 374 / IMG_H, rot: -0.18 },
    ];
    const LENS_RX_IMG = 29;
    const LENS_RY_IMG = 17;

    /* Kolory powieki próbkowane z obrazu */
    const SKIN = 'rgb(187,119,86)';
    const LASH = 'rgba(28,10,2,0.85)';

    /* Przelicz środek oka i skalę na współrzędne ekranu */
    function eyeToScreen(e, vw, vh) {
      const aspect = IMG_W / IMG_H;
      let dw, dh;
      if (vw / vh > aspect) { dh = vh; dw = dh * aspect; }
      else                   { dw = vw; dh = dw / aspect; }
      const ox = (vw - dw) * OBJ_X;
      const oy = (vh - dh) * OBJ_Y;

      let sx = ox + e.ix * dw;
      let sy = oy + e.iy * dh;
      /* scale(1.10) ze środka ekranu */
      sx = (sx - vw / 2) * CSS_S + vw / 2;
      sy = (sy - vh / 2) * CSS_S + vh / 2;
      /* translateY(13%) */
      sy += CSS_TY * vh;

      const imgScale = dw / IMG_W;
      return {
        x:  sx,
        y:  sy,
        rx: LENS_RX_IMG * imgScale * CSS_S,
        ry: LENS_RY_IMG * imgScale * CSS_S,
      };
    }

    /* Stan maszyny mrugania */
    let p = 0;           /* progress: 0=open, 1=closed */
    let phase = 'idle';
    let lastTs = null;
    let holdTid = null;
    let rafId;

    function scheduleNext() {
      phase = 'idle';
      holdTid = setTimeout(() => { phase = 'closing'; },
                            3000 + Math.random() * 3000);
    }
    scheduleNext();

    function resize() {
      canvas.width  = window.innerWidth;
      canvas.height = window.innerHeight;
    }
    resize();
    window.addEventListener('resize', resize);

    function tick(ts) {
      if (!lastTs) lastTs = ts;
      const dt = Math.min((ts - lastTs) / 1000, 0.05);
      lastTs = ts;

      if (phase === 'closing') {
        p = Math.min(1, p + dt / 0.07);   /* 70 ms zamknięcie */
        if (p >= 1) {
          phase = 'hold';
          holdTid = setTimeout(() => { phase = 'opening'; }, 40);
        }
      } else if (phase === 'opening') {
        p = Math.max(0, p - dt / 0.09);   /* 90 ms otwieranie */
        if (p <= 0) {
          /* okazjonalne podwójne mrugnięcie */
          if (Math.random() < 0.20) {
            holdTid = setTimeout(() => { phase = 'closing'; },
                                  220 + Math.random() * 80);
            phase = 'idle';
          } else {
            scheduleNext();
          }
        }
      }

      ctx.clearRect(0, 0, canvas.width, canvas.height);

      if (p > 0.005) {
        const vw = canvas.width, vh = canvas.height;
        for (const e of EYES) {
          const { x, y, rx, ry } = eyeToScreen(e, vw, vh);
          const rot = e.rot || 0;

          ctx.save();
          ctx.translate(x, y);
          ctx.rotate(rot);

          /* CLIP: kształt migdałowy — szpiczasty w kącikach jak oko */
          ctx.beginPath();
          ctx.moveTo(-rx, 0);
          ctx.bezierCurveTo(-rx * 0.45, -ry, rx * 0.45, -ry,  rx, 0);
          ctx.bezierCurveTo( rx * 0.45,  ry, -rx * 0.45, ry, -rx, 0);
          ctx.closePath();
          ctx.clip();

          /* Górna powieka: fillRect od góry — clip tworzy migdałowy kształt */
          const drop = ry * 2 * p;
          ctx.fillStyle = SKIN;
          ctx.fillRect(-rx, -ry, rx * 2, drop);

          /* Linia rzęs */
          if (p > 0.15) {
            ctx.fillStyle = LASH;
            ctx.fillRect(-rx, -ry + drop - 2, rx * 2, 2.5);
          }

          /* Dolna powieka */
          const rise = ry * 0.4 * p;
          ctx.fillStyle = SKIN;
          ctx.fillRect(-rx, ry - rise, rx * 2, rise);

          ctx.restore();
        }
      }

      rafId = requestAnimationFrame(tick);
    }
    rafId = requestAnimationFrame(tick);

    return () => {
      cancelAnimationFrame(rafId);
      clearTimeout(holdTid);
      window.removeEventListener('resize', resize);
    };
  }, []);

  return (
    <canvas
      ref={canvasRef}
      aria-hidden="true"
      style={{ position: 'absolute', inset: 0, zIndex: 5, pointerEvents: 'none' }}
    />
  );
}

/* ─── HOME: scena złożona z osobnych warstw assetów ─── */
function HomeSceneLayers() {
  return (
    <div className="home-scene-layers" aria-hidden="true">
      {/* warstwa 1 — niebo */}
      <img className="scene-layer sl-niebo"  src="assets/niebo.png"        alt="" draggable="false" />
      {/* warstwa 2 — główne tło sceny */}
      <img className="scene-layer sl-tlo"    src="assets/tlo.png"          alt="" draggable="false" />
      {/* warstwa 3 — postać główna (statyczna) */}
      <img className="scene-layer sl-postac" src="assets/postac-glowna.png" alt="" draggable="false" />

      {/* warstwa 4 — shimmer włosów (tylko obszar włosów, nie postać) */}
      <div className="hair-wind-overlay" aria-hidden="true" />
    </div>
  );
}

/* ─── HOME: animowane chmury w tle nieba ─── */
function HomeChmury() {
  return (
    <div className="chmury-layer" aria-hidden="true">
      {/* chmura1.png — główna, wysoko przy górze */}
      <div className="chmura-wrap ch2">
        <img src="assets/chmura1.png" alt="" draggable="false" />
      </div>
      {/* chmura2.png — mniejsza, lekko niżej */}
      <div className="chmura-wrap ch3">
        <img src="assets/chmura2.png" alt="" draggable="false" />
      </div>
    </div>
  );
}

/* ─── Stopka strony głównej ─── */
function HomeFooter({ lang }) {
  return (
    <footer className="home-footer">
      <div className="home-footer-inner">
        <span className="footer-name">Emilia Małecka</span>
        <span className="footer-sep">|</span>
        <span className="footer-role">Product Designer &amp; Builder</span>
        <span className="footer-sep">|</span>
        <a href="mailto:emilkamalecka34@gmail.com" className="footer-link">emilkamalecka34@gmail.com</a>
        <span className="footer-sep">|</span>
        <a href="https://linkedin.com/in/emilia-malecka" target="_blank" rel="noreferrer" className="footer-link">LinkedIn</a>
        <span className="footer-sep">|</span>
        <span className="footer-copy">© {new Date().getFullYear()}</span>
      </div>
    </footer>
  );
}

/* ─── HOME scene ─── */
function HomeScene({ lang, headline, onNav, ambient }) {
  const t = window.I18N[lang].home;
  const [head1, head2] = splitHeadline(headline);

  return (
    <React.Fragment>
      <HomeSceneLayers />

      <HomeChmury />

      <HomeKwiaty />

      <div className="home-lanterns">
        <div className={"lantern l1" + (ambient ? " flicker" : "")}></div>
        <div className={"lantern l2 f2" + (ambient ? " flicker" : "")}></div>
      </div>

      <AmbientLayers ambient={ambient} />

      <div className="hero-text">
        <h1>
          <span className="head1">{head1}</span>
          <em>{head2}</em>
        </h1>
        <p className="hero-tags">
          <span className="tag-word">Product Builder</span>
          <span className="tag-dot">&nbsp;&nbsp;•&nbsp;&nbsp;</span>
          <span className="tag-word">UX</span>
          <span className="tag-dot">&nbsp;&nbsp;•&nbsp;&nbsp;</span>
          <span className="tag-word">Analysis</span>
        </p>
        <p className="sub">{t.sub}</p>
      </div>

      <div className="signpost-overlay" aria-label="Navigation">
        <button className="sign s1" onClick={() => onNav('map')}     aria-label={t.nav.works}>   <span className="sign-label">{t.nav.works}</span></button>
        <button className="sign s2" onClick={() => onNav('about')}   aria-label={t.nav.about}>   <span className="sign-label">{t.nav.about}</span></button>
        <button className="sign s3" onClick={() => onNav('contact')} aria-label={t.nav.contact}> <span className="sign-label">{t.nav.contact}</span></button>
      </div>

      <div className="home-mobile-nav">
        <button onClick={() => onNav('map')}>{t.nav.works} →</button>
        <button onClick={() => onNav('about')}>{t.nav.about} →</button>
        <button onClick={() => onNav('contact')}>{t.nav.contact} →</button>
      </div>

    </React.Fragment>
  );
}

/* ─── Character idle animation ─── */
function CharacterIdle() {
  const closeRef = useRef(null);

  useEffect(() => {
    let t;

    function openEyes() {
      const el = closeRef.current;
      if (!el) return;
      el.style.transition = 'opacity 110ms ease-out';
      el.style.opacity    = '0';
    }

    function blink(isDouble) {
      const el = closeRef.current;
      if (!el) return;
      /* close */
      el.style.transition = 'opacity 70ms ease-in';
      el.style.opacity    = '1';
      setTimeout(() => {
        openEyes();
        if (!isDouble && Math.random() < 0.15) {
          /* double-blink: second blink ~320 ms later */
          setTimeout(() => blink(true), 320);
        }
        /* schedule next blink */
        t = setTimeout(() => blink(false), 3200 + Math.random() * 4800);
      }, 65);
    }

    /* first blink after 1.5–3.5 s */
    t = setTimeout(() => blink(false), 1500 + Math.random() * 2000);
    return () => clearTimeout(t);
  }, []);

  return (
    <div className="char-idle-wrap" aria-hidden="true">
      {/* SVG filter: gentle hair-wind turbulence */}
      <svg style={{position:'absolute',width:0,height:0,overflow:'hidden'}}>
        <defs>
          <filter id="char-wind" x="-8%" y="-8%" width="116%" height="116%"
                  colorInterpolationFilters="linearRGB">
            <feTurbulence type="fractalNoise"
                          baseFrequency="0.006 0.014"
                          numOctaves="3" seed="4" result="turb">
              <animate attributeName="seed" from="1" to="28"
                       dur="20s" repeatCount="indefinite"/>
            </feTurbulence>
            <feDisplacementMap in="SourceGraphic" in2="turb"
                               scale="3.5"
                               xChannelSelector="R" yChannelSelector="G"/>
          </filter>
        </defs>
      </svg>

      {/* breathing / sway wrapper */}
      <div className="char-breathe-wrap">
        {/* wind-filter wrapper (separate from transform for GPU) */}
        <div className="char-wind-wrap">
          <img src="assets/Person.png"
               className="char-img" alt="" draggable="false"/>
          <img src="assets/Person close eye.png"
               className="char-img char-closed" ref={closeRef}
               alt="" draggable="false"/>
        </div>
      </div>
    </div>
  );
}

/* ─── Character idle animation FULL — używane gdy postac.png dostępny ─── */
function CharacterIdleFull_UNUSED() {
  const canvasRef = useRef(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    /*
     * Eye positions in the ORIGINAL scene-home.png (1672 × 941 px).
     * Measured via background-size:cover math against 1396×591 viewport.
     * lensR = glasses lens radius in image pixels.
     */
    const EYES_IMG = [
      { ix: 937, iy: 308, lensR: 27 }, // left lens (viewer's left)
      { ix: 1012, iy: 300, lensR: 25 }, // right lens (viewer's right)
    ];
    const IMG_W = 1672, IMG_H = 941;

    /* Maps image-space coords → current viewport coords */
    function vpEyes() {
      const vpW = window.innerWidth, vpH = window.innerHeight;
      const scale = Math.max(vpW / IMG_W, vpH / IMG_H);
      const offX  = (vpW - IMG_W * scale) / 2;
      const offY  = (vpH - IMG_H * scale) / 2;
      return EYES_IMG.map(e => ({
        x:     e.ix * scale + offX,
        y:     e.iy * scale + offY,
        lensR: e.lensR * scale,
      }));
    }

    function resize() {
      canvas.width  = window.innerWidth;
      canvas.height = window.innerHeight;
    }
    resize();
    window.addEventListener('resize', resize);

    const ctx = canvas.getContext('2d');

    /* Skin tone sampled from character face */
    const SKIN_CLR = '#c8916b';
    const LASH_CLR = '#1e0e05';

    function drawBlink(progress) {
      /* progress: 0 = fully open, 1 = fully closed */
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      if (progress <= 0.01) return;

      vpEyes().forEach(({ x, y, lensR }) => {
        const rx = lensR * 0.80; // lens x-radius
        const ry = lensR * 0.74; // lens y-radius

        ctx.save();
        /* Clip drawing to the glasses lens ellipse */
        ctx.beginPath();
        ctx.ellipse(x, y, rx, ry, 0, 0, Math.PI * 2);
        ctx.clip();

        /* Upper eyelid sweeps down from top of lens */
        const lidH = ry * 2 * progress;
        ctx.fillStyle = SKIN_CLR;
        ctx.fillRect(x - rx, y - ry, rx * 2, lidH + 1);

        /* Thin lash line at lower edge of eyelid */
        if (progress > 0.20) {
          ctx.fillStyle = LASH_CLR;
          const lashH = Math.max(1, 1.5 * (lensR / 22)); // scale with lensR
          ctx.fillRect(x - rx, y - ry + lidH - lashH, rx * 2, lashH + 1);
        }

        ctx.restore();
      });
    }

    /* Blink state machine */
    let progress    = 0;
    let phase       = 'idle'; // idle | closing | hold | opening
    let nextBlink   = Date.now() + 2000 + Math.random() * 2500;
    let holdTimer   = null;
    let rafId;

    const CLOSE_SPD = 0.13; // ~8 frames ≈ 130 ms to close
    const OPEN_SPD  = 0.09; // ~11 frames ≈ 180 ms to open (slightly slower)
    const HOLD_MS   = 55;   // ms eyelid stays fully closed

    function tick() {
      const now = Date.now();

      if (phase === 'idle' && now >= nextBlink) phase = 'closing';

      if (phase === 'closing') {
        progress = Math.min(1, progress + CLOSE_SPD);
        drawBlink(progress);
        if (progress >= 1) {
          phase = 'hold';
          holdTimer = setTimeout(() => { phase = 'opening'; }, HOLD_MS);
        }
      } else if (phase === 'hold') {
        drawBlink(1);
      } else if (phase === 'opening') {
        progress = Math.max(0, progress - OPEN_SPD);
        drawBlink(progress);
        if (progress <= 0) {
          phase = 'idle';
          ctx.clearRect(0, 0, canvas.width, canvas.height);
          /* Occasionally do a double-blink: 15% chance */
          const gap = Math.random() < 0.15
            ? 400 + Math.random() * 300
            : 3000 + Math.random() * 4000;
          nextBlink = now + gap;
        }
      }

      rafId = requestAnimationFrame(tick);
    }

    rafId = requestAnimationFrame(tick);

    return () => {
      cancelAnimationFrame(rafId);
      clearTimeout(holdTimer);
      window.removeEventListener('resize', resize);
    };
  }, []);

  return (
    <React.Fragment>
      {/* Breathing layer: pixel-identical copy of illo, soft-masked to
          the character's torso area, animated with subtle scaleY */}
      <div className="char-breathe-layer" aria-hidden="true"/>
      {/* Blink canvas: transparent except during eyelid animation */}
      <canvas ref={canvasRef} className="char-blink-canvas" aria-hidden="true"/>
    </React.Fragment>
  );
}
/* END CharacterIdleFull_UNUSED */


/* ─── MapPathGlow: świecące kropki wzdłuż ścieżki na mapie ─── */
function MapPathGlow() {
  const canvasRef = React.useRef(null);

  React.useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');

    /* Punkty ścieżki jako % viewport (wzdłuż krętej drogi od dołu do szczytu) */
    const PATH = [
      [29,89],[31,85],[33,81],[36,76],[38,72],[40,68],
      [41.7,63],[44,59],[47,56],[51,53],[55,51],
      [59,49],[63,48],[67,47],[69.8,46.7],
      [71,43],[72,39],[72.5,35],[72.5,31],[72,27],
      [71.8,23],[71.8,21],
    ];

    function resize() {
      canvas.width  = window.innerWidth;
      canvas.height = window.innerHeight;
    }
    resize();
    window.addEventListener('resize', resize);

    let rafId;
    const start = performance.now();

    function tick(now) {
      const t = (now - start) / 1000;
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      const vw = canvas.width, vh = canvas.height;

      PATH.forEach(([xp, yp], i) => {
        const x = xp / 100 * vw;
        const y = yp / 100 * vh;

        /* Każda kropka pulsuje z lekkim przesunięciem fazowym */
        const phase = t * 1.4 + i * 0.38;
        const pulse = 0.45 + 0.55 * (0.5 + 0.5 * Math.sin(phase));

        const r = 5 * pulse;

        /* Zewnętrzna poświata */
        const glow = ctx.createRadialGradient(x, y, 0, x, y, r * 4.5);
        glow.addColorStop(0,   `rgba(255,220,120,${0.55 * pulse})`);
        glow.addColorStop(0.4, `rgba(255,190,80,${0.28 * pulse})`);
        glow.addColorStop(1,   'rgba(255,160,50,0)');
        ctx.beginPath();
        ctx.arc(x, y, r * 4.5, 0, Math.PI * 2);
        ctx.fillStyle = glow;
        ctx.fill();

        /* Jasny środek */
        ctx.beginPath();
        ctx.arc(x, y, r, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(255,240,180,${0.85 * pulse})`;
        ctx.fill();
      });

      rafId = requestAnimationFrame(tick);
    }
    rafId = requestAnimationFrame(tick);

    return () => {
      cancelAnimationFrame(rafId);
      window.removeEventListener('resize', resize);
    };
  }, []);

  return (
    <canvas
      ref={canvasRef}
      aria-hidden="true"
      style={{ position:'absolute', inset:0, zIndex:9, pointerEvents:'none' }}
    />
  );
}

/* ─── Efekt wody: wodospad + rzeka ─── */
function MapWaterFx() {
  const canvasRef = React.useRef(null);

  React.useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');

    function resize() {
      canvas.width  = window.innerWidth;
      canvas.height = window.innerHeight;
    }
    resize();
    window.addEventListener('resize', resize);

    let rafId;
    const start = performance.now();

    /* Losowe prążki wodospadu */
    const streaks = Array.from({length: 14}, (_, i) => ({
      x:    0.850 + (Math.random() * 0.015),
      yOff: Math.random(),
      w:    0.5 + Math.random() * 0.7,
      spd:  0.9 + Math.random() * 0.6,
    }));


    function tick(now) {
      const t = (now - start) / 1000;
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      const vw = canvas.width, vh = canvas.height;
      ctx.globalCompositeOperation = 'screen';

      /* ── Wodospad: pionowe prążki spływające w dół ── */
      const wfX0 = 0.848 * vw, wfY0 = 0.33 * vh;
      const wfH  = 0.096 * vh;

      streaks.forEach(s => {
        const sx = s.x * vw;
        /* Prążek przesuwa się od góry do dołu w pętli */
        const offset = ((t * s.spd * 0.6 + s.yOff) % 1.0);
        const sy = wfY0 + offset * wfH;
        const segLen = wfH * 0.35;

        const grad = ctx.createLinearGradient(sx, sy, sx, sy + segLen);
        grad.addColorStop(0,   'rgba(180,220,255,0)');
        grad.addColorStop(0.3, 'rgba(200,235,255,0.45)');
        grad.addColorStop(0.7, 'rgba(210,240,255,0.45)');
        grad.addColorStop(1,   'rgba(180,220,255,0)');

        ctx.beginPath();
        ctx.moveTo(sx, sy);
        ctx.lineTo(sx, sy + segLen);
        ctx.strokeStyle = grad;
        ctx.lineWidth = s.w;
        ctx.stroke();
      });


      ctx.globalCompositeOperation = 'source-over';
      rafId = requestAnimationFrame(tick);
    }
    rafId = requestAnimationFrame(tick);

    return () => {
      cancelAnimationFrame(rafId);
      window.removeEventListener('resize', resize);
    };
  }, []);

  return (
    <canvas ref={canvasRef} aria-hidden="true"
      style={{ position:'absolute', inset:0, zIndex:8, pointerEvents:'none' }} />
  );
}

/* ─── Dym z komina na mapie ─── */
function MapSmoke() {
  /* Pozycja komina jako % viewportu (dom przy waypoincie 1) */
  const CHIMNEY_X = 53.8;
  const CHIMNEY_Y = 65.2;

  return (
    <div className="map-smoke-wrap" aria-hidden="true"
         style={{ left: CHIMNEY_X + '%', top: CHIMNEY_Y + '%' }}>
      {[0,1,2,3,4].map(i => (
        <div key={i} className="smoke-puff" style={{ '--i': i }} />
      ))}
    </div>
  );
}

function MapScene({ lang, headline, projects, onBack, onPick, ambient }) {
  const t = window.I18N[lang].map;
  const [head1, head2] = splitMapHeadline(headline);

  return (
    <React.Fragment>
      <div className="illo" data-img="map"></div>

      <MapSmoke />
      <MapWaterFx />
      <AmbientLayers ambient={ambient} />

      <div className="map-text">
        <h1>{head1}<em>{head2}</em></h1>

      </div>

      {/* kwiaty w prawym dolnym rogu mapy */}
      <div className="kwiat-mapa-wrap" aria-hidden="true">
        <img src="assets/kwiatmapa.png?v=4" alt="" draggable="false" />
      </div>
      <div className="kwiat-mapa-wrap kwiat-mapa-2" aria-hidden="true">
        <img src="assets/kwiatmapa.png?v=4" alt="" draggable="false" />
      </div>
      <div className="kwiat-mapa-wrap kwiat-mapa-3" aria-hidden="true">
        <img src="assets/kwiatmapa.png?v=4" alt="" draggable="false" />
      </div>

      <button className="sign map-back-sign" onClick={onBack} aria-label={t.back}>
        <span className="sign-label">{t.back}</span>
      </button>

      <div className="waypoints">
        {projects.map((p, i) => {
          const data = p[lang] || p.pl;
          return (
            <button
              key={p.id}
              className="wp"
              style={{ left: p.pos.x + '%', top: p.pos.y + '%' }}
              onClick={() => onPick(p.id)}
              aria-label={p.name}
            >
              {String(i + 1).padStart(2, '0')}
              <div className="wp-card">
                <h3>{p.name}</h3>
                <p>{data.tagline}</p>
                <span className="cta">{t.cta} →</span>
              </div>
            </button>
          );
        })}
      </div>
    </React.Fragment>
  );
}

/* ─── CASE STUDY sheet ─── */
function CaseStudy({ lang, project, projects, onBack, onPick }) {
  const tt = window.I18N[lang].case;
  if (!project) return null;
  const d = project[lang] || project.pl;
  const idx = projects.findIndex(p => p.id === project.id);
  const next = projects[(idx + 1) % projects.length];

  return (
    <div className="sheet-inner">
      <button className="sheet-close" onClick={onBack}>
        ✕
      </button>
      <p className="eyebrow">{String(idx + 1).padStart(2, '0')} · Case Study</p>
      <h1>{project.name}</h1>
      <p className="lede">{d.tagline}</p>

      <dl className="case-meta">
        <div><dt>{tt.role}</dt><dd>{d.role}</dd></div>
        <div><dt>{tt.year}</dt><dd>{d.year}</dd></div>
        <div><dt>{tt.duration}</dt><dd>{d.duration}</dd></div>
        <div><dt>{tt.tools}</dt><dd>{d.tools.join(', ')}</dd></div>
      </dl>

      <h2>{tt.problem}</h2><p>{d.problem}</p>
      <h2>{tt.process}</h2><p>{d.process}</p>
      <h2>{tt.result}</h2><p>{d.result}</p>

      <h2>{tt.gallery}</h2>
      <div className="gallery">
        <div className="img">{project.name} · screen 01</div>
        <div className="img">{project.name} · screen 02</div>
        <div className="img tall">{project.name} · detail</div>
        <div className="img tall">{project.name} · system</div>
      </div>

      <div className="next-link">
        <span className="label">{tt.next}</span>
        <button onClick={() => onPick(next.id)}>
          <span className="name">{next.name} →</span>
          <span className="label">{tt.goNext}</span>
        </button>
      </div>
    </div>
  );
}

/* ─── ABOUT sheet ─── */
function About({ lang, onBack }) {
  const a = window.I18N[lang].about;
  return (
    <div className="sheet-inner">
      <button className="sheet-close" onClick={onBack}>
        ✕
      </button>
      <p className="eyebrow">{a.eyebrow}</p>
      <h1>{a.h1}</h1>
      <p className="lede">{a.lede}</p>

      <div className="about-grid" style={{ marginTop: 30 }}>
        <div>
          {a.bio.map((p, i) => <p key={i}>{p}</p>)}
          <h2 style={{ fontSize: 22, marginTop: 28 }}>{a.skillsTitle}</h2>
          <div className="toolset">
            {a.skills.map(s => <span key={s}>{s}</span>)}
          </div>
          <h2 style={{ fontSize: 22, marginTop: 28 }}>{a.toolsTitle}</h2>
          <div className="toolset">
            {a.tools.map(s => <span key={s}>{s}</span>)}
          </div>
        </div>
        <div className="photo">{lang === 'pl' ? 'Zdjęcie · do uzupełnienia' : 'Photo · placeholder'}</div>
      </div>
    </div>
  );
}

/* ─── CONTACT sheet ─── */
function Contact({ lang, onBack }) {
  const c = window.I18N[lang].contact;
  const [copied, setCopied] = React.useState(false);

  function copyPhone(e) {
    e.preventDefault();
    navigator.clipboard.writeText('+48786105242').then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    });
  }

  return (
    <div className="sheet-inner">
      <button className="sheet-close" onClick={onBack}>
        ✕
      </button>
      <h1>{c.h1}</h1>
      <p className="lede">{c.lede}</p>

      <div className="contact-list" style={{ marginTop: 30 }}>
        <a href="#" onClick={copyPhone}>
          <span className="label">{copied ? (lang === 'pl' ? 'Skopiowano!' : 'Copied!') : c.labels.phone}</span>
          786 — 105 — 242
        </a>
        <a href="https://mail.google.com/mail/?view=cm&to=emilia.malecka36@gmail.com" target="_blank" rel="noreferrer">
          <span className="label">{c.labels.email}</span>
          emilia.malecka36@gmail.com
        </a>
        <a href="https://www.linkedin.com/in/emilia-ma%C5%82ecka" target="_blank" rel="noreferrer">
          <span className="label">{c.labels.linkedin}</span>
          LinkedIn Emilia Małecka
        </a>
      </div>
    </div>
  );
}

/* ─── ROOT ─── */
/* ── Hash helpers ── */
function readHash() {
  const h = window.location.hash.slice(1);
  if (h === 'map')     return { screen: 'map',     project: null };
  if (h === 'about')   return { screen: 'about',   project: null };
  if (h === 'contact') return { screen: 'contact', project: null };
  if (h.startsWith('case/')) {
    const p = (window.PROJECTS || []).find(p => p.id === h.slice(5));
    if (p) return { screen: 'case', project: p };
  }
  return { screen: 'home', project: null };
}

function App() {
  const [tw, setTweak] = useTweaks(TWEAK_DEFAULTS);
  const [lang, setLang] = useState('pl');
  const [screen, setScreen] = useState(() => readHash().screen);
  const [project, setProject] = useState(() => readHash().project);


  const projects = useMemo(
    () => window.PROJECTS.slice(0, Math.max(1, Math.min(window.PROJECTS.length, tw.projectCount))),
    [tw.projectCount]
  );

  const homeHeadline = lang === 'pl' ? tw.headlineHomePL : tw.headlineHomeEN;
  const mapHeadline  = lang === 'pl' ? tw.headlineMapPL  : tw.headlineMapEN;

  const isOverlay = screen === 'case' || screen === 'about' || screen === 'contact';
  const baseScene = isOverlay ? (screen === 'case' ? 'map' : 'home') : screen;

  const goHome    = useCallback(() => {
    if (burnRef.current) return;
    burnRef.current = true;
    const worldEl = document.querySelector('.world');
    const activeEl = document.querySelector('.scene.active');
    const homeEl = document.querySelectorAll('.scene')[0];
    if (!homeEl || activeEl === homeEl) { setScreen('home'); setProject(null); burnRef.current = null; return; }
    if (worldEl) worldEl.classList.add('is-transitioning');
    homeEl.style.cssText = 'opacity:0;visibility:visible;transform:none;filter:none;z-index:3;transition:none;';
    requestAnimationFrame(() => {
      if (activeEl) { activeEl.style.transition = 'opacity 380ms ease'; activeEl.style.opacity = '0'; }
      homeEl.style.transition = 'opacity 380ms ease';
      homeEl.style.opacity = '1';
      setTimeout(() => {
        setScreen('home'); setProject(null); burnRef.current = null;
        requestAnimationFrame(() => requestAnimationFrame(() => {
          if (activeEl) activeEl.style.cssText = '';
          homeEl.style.cssText = '';
          if (worldEl) worldEl.classList.remove('is-transitioning');
        }));
      }, 400);
    });
  }, []);
  const openCase  = (id) => { setProject(window.PROJECTS.find(p => p.id === id)); setScreen('case'); };
  const closeSheet = () => { setScreen(project ? 'map' : 'home'); };

  const burnRef = useRef(null);

  const startBurnReveal = useCallback((target) => {
    if (burnRef.current) return;
    burnRef.current = true;

    const worldEl = document.querySelector('.world');
    const homeEl  = document.querySelector('.scene.active');
    const mapEl   = document.querySelector('.scene[data-pos="map"]');

    if (!mapEl) { setScreen(target); burnRef.current = null; return; }
    if (worldEl) worldEl.classList.add('is-transitioning');

    /* Mapa widoczna pod spodem */
    mapEl.style.cssText = 'opacity:0;visibility:visible;transform:none;filter:none;z-index:3;transition:none;';

    requestAnimationFrame(() => {
      /* Home zanika */
      if (homeEl) {
        homeEl.style.transition = 'opacity 450ms ease';
        homeEl.style.opacity = '0';
      }
      /* Mapa pojawia się */
      mapEl.style.transition = 'opacity 450ms ease';
      mapEl.style.opacity = '1';

      setTimeout(() => {
        setScreen(target);
        burnRef.current = null;
        requestAnimationFrame(() => requestAnimationFrame(() => {
          if (homeEl) homeEl.style.cssText = '';
          mapEl.style.cssText = '';
          if (worldEl) worldEl.classList.remove('is-transitioning');
        }));
      }, 470);
    });
  }, []);

  const onNav = (where) => {
    if (where === 'map') {
      if (screen === 'home') { startBurnReveal('map'); return; }
      setScreen('map');
    }
    else if (where === 'about')   setScreen('about');
    else if (where === 'contact') setScreen('contact');
  };

  useEffect(() => {
    const onKey = (e) => {
      if (e.key === 'Escape') {
        if (isOverlay) closeSheet();
        else if (screen === 'map') goHome();
      }
    };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [screen, isOverlay]);

  /* Sync URL hash przy każdej zmianie widoku */
  useEffect(() => {
    if (screen === 'home')                       window.location.hash = '';
    else if (screen === 'case' && project)       window.location.hash = 'case/' + project.id;
    else                                         window.location.hash = screen;
  }, [screen, project]);

  /* Obsługa przycisku Wstecz / hashchange */
  useEffect(() => {
    const onHash = () => {
      const { screen: s, project: p } = readHash();
      setScreen(s);
      setProject(p);
    };
    window.addEventListener('hashchange', onHash);
    return () => window.removeEventListener('hashchange', onHash);
  }, []);




  const sceneClass = (id) => {
    const classes = ['scene'];
    if (id === baseScene && !isOverlay) classes.push('active');
    /* case study: mapa zostaje active — glass panel sam przyciemnia backdrop */
    else if (id === baseScene && screen === 'case') classes.push('active');
    else if (id === baseScene && isOverlay) classes.push('dim');
    return classes.join(' ');
  };
  const sceneAttr = (id) => (id === baseScene ? undefined : (id === 'home' ? 'home' : 'map'));

  useEffect(() => {
    if (screen !== 'home') {
      const w = document.querySelector('.world');
      if (w) w.scrollTop = 0;
    }
  }, [screen]);

  /* Przedłuż sl-tlo w dół aby scroll odkrył obciętą dolną część */
  useEffect(() => {
    if (screen !== 'home') return;

    function fixTlo() {
      const tlo = document.querySelector('.sl-tlo');
      if (!tlo || !tlo.naturalWidth) return;
      const iw = tlo.naturalWidth, ih = tlo.naturalHeight;
      const vw = window.innerWidth, vh = window.innerHeight;
      const scale = Math.max(vw / iw, vh / ih);
      const dispH = ih * scale;
      if (dispH <= vh + 1) return; // obraz mieści się w całości, nic do zrobienia
      const extra = Math.ceil((dispH - vh) / 2);
      tlo.style.height = (vh + extra) + 'px';
      tlo.style.objectPosition = 'center bottom';
      tlo.style.bottom = 'auto';
      /* zaktualizuj margines stopki żeby scroll był wystarczający */
      const footer = document.querySelector('.home-footer');
      if (footer) footer.style.marginTop = (vh + extra) + 'px';
    }

    const tlo = document.querySelector('.sl-tlo');
    if (!tlo) return;
    if (tlo.complete && tlo.naturalWidth) fixTlo();
    else tlo.addEventListener('load', fixTlo);
    window.addEventListener('resize', fixTlo);

    return () => {
      window.removeEventListener('resize', fixTlo);
      const t = document.querySelector('.sl-tlo');
      if (t) { t.style.height = ''; t.style.objectPosition = ''; t.style.bottom = ''; }
      const f = document.querySelector('.home-footer');
      if (f) f.style.marginTop = '';
    };
  }, [screen]);

  return (
    <div className={"world" + (tw.ambient ? "" : " no-anim") + (screen === 'home' ? " screen-home" : "")}>
      <div className={sceneClass('home')} data-pos={sceneAttr('home')}>
        <HomeScene lang={lang} headline={homeHeadline} onNav={onNav} ambient={tw.ambient} />
      </div>

      <div className={sceneClass('map')} data-pos={sceneAttr('map')}>
        <MapScene lang={lang} headline={mapHeadline} projects={projects} onBack={goHome} onPick={openCase} ambient={tw.ambient} />
      </div>

      {/* ── Glass overlay — case study ── */}
      {screen === 'case' && (
        <div className="case-study-overlay" onClick={closeSheet}>
          <div className="case-study-glass-panel" onClick={e => e.stopPropagation()}>
            <button className="case-glass-close" onClick={closeSheet} aria-label="Zamknij">✕</button>
          </div>

          {/* Postać — nad panelem, poza blur, pełna ostrość */}
          <img
            src="assets/person%20use%20case1.png?v=7"
            className="case-study-character"
            alt=""
            draggable="false"
            onClick={e => e.stopPropagation()}
          />
        </div>
      )}

      {/* ── Sheet — about / contact ── */}
      <div className={"sheet-veil" + ((screen === 'about' || screen === 'contact') ? " show" : "")} onClick={closeSheet}></div>
      <div className={"sheet" + ((screen === 'about' || screen === 'contact') ? " show" : "")}>
        {screen === 'about'   && <About    lang={lang} onBack={goHome} />}
        {screen === 'contact' && <Contact  lang={lang} onBack={goHome} />}
      </div>

      {screen === 'home' && (
        <footer className="home-footer">
          <span>© {new Date().getFullYear()} Emilia Małecka</span>
          <span className="home-footer-dot">·</span>
          <span>{lang === 'pl' ? 'Wszelkie prawa zastrzeżone' : 'All rights reserved'}</span>
        </footer>
      )}

      <BurnRevealSVG />
      <Chrome lang={lang} setLang={setLang} onHome={goHome} />

      <TweaksPanel>
        <TweakSection label={lang === 'pl' ? 'Nagłówki' : 'Headlines'} />
        <TweakText  label={lang === 'pl' ? 'Strona główna · PL' : 'Home · PL'}
                    value={tw.headlineHomePL}
                    onChange={(v) => setTweak('headlineHomePL', v)} />
        <TweakText  label={lang === 'pl' ? 'Strona główna · EN' : 'Home · EN'}
                    value={tw.headlineHomeEN}
                    onChange={(v) => setTweak('headlineHomeEN', v)} />
        <TweakText  label={lang === 'pl' ? 'Mapa · PL' : 'Map · PL'}
                    value={tw.headlineMapPL}
                    onChange={(v) => setTweak('headlineMapPL', v)} />
        <TweakText  label={lang === 'pl' ? 'Mapa · EN' : 'Map · EN'}
                    value={tw.headlineMapEN}
                    onChange={(v) => setTweak('headlineMapEN', v)} />

        <TweakSection label={lang === 'pl' ? 'Mapa' : 'Map'} />
        <TweakSlider label={lang === 'pl' ? 'Liczba projektów' : 'Project count'}
                     value={tw.projectCount} min={1} max={window.PROJECTS.length} step={1}
                     onChange={(v) => setTweak('projectCount', v)} />

        <TweakSection label={lang === 'pl' ? 'Atmosfera' : 'Ambient'} />
        <TweakToggle label={lang === 'pl' ? 'Migotanie latarni' : 'Lantern flicker'}
                     value={tw.ambient}
                     onChange={(v) => setTweak('ambient', v)} />
      </TweaksPanel>
    </div>
  );
}

ReactDOM.createRoot(document.getElementById('root')).render(<App />);
