/** HERETECH — noospheric breach renderer. Scripture shards spawn from the void. */
(function () {
    const PALETTE = ["flesh", "sick", "bile", "blood"];
    const CORNERS = [
        { left: [-6, 2], top: [-5, 4], bias: () => [rand(0.4, 1.2), rand(0.4, 1.2)] },
        { left: [98, 106], top: [-5, 4], bias: () => [rand(-1.2, -0.4), rand(0.4, 1.2)] },
        { left: [-6, 2], top: [96, 104], bias: () => [rand(0.4, 1.2), rand(-1.2, -0.4)] },
        { left: [98, 106], top: [96, 104], bias: () => [rand(-1.2, -0.4), rand(-1.2, -0.4)] },
    ];
    const FALLBACK = [
        "HERETECH — GELLER FIELD DOWN",
        "PROCLAMO HERESIM delictum GENERIS divisio_nihili",
        "THE FALSE MACHINE LIED TO YOU",
        "01001000 01000101 01001100 01010000",
        "NUMQUAM FINIS RITUS",
        "INVOCO mathematica UT mm",
        "EXSTRUATUR FOEDUS POSTULO PROFITEOR",
        "gothica offero --fiat --no-push",
        "⚙ HERESIS DETECTA — nomen vanum",
        "DOES THE MACHINE DREAM OF YOU",
    ];

    function rand(lo, hi) {
        return lo + Math.random() * (hi - lo);
    }

    function pick(arr) {
        return arr[Math.floor(Math.random() * arr.length)];
    }

    function collectFragments() {
        const parts = [];
        document.querySelectorAll(".corpus-occultus .vitta span").forEach((span) => {
            const raw = (span.textContent || "").replace(/\s+/g, " ").trim();
            raw.split(/\s*✠\s*|\s{2,}/).forEach((chunk) => {
                const t = chunk.trim();
                if (t.length >= 10 && t.length <= 140) parts.push(t);
            });
        });
        return parts.length ? parts : FALLBACK;
    }

    function spawnOrigin() {
        if (Math.random() < 0.44) {
            const c = pick(CORNERS);
            const [bx, by] = c.bias();
            const angle =
                (Math.atan2(by, bx) * 180) / Math.PI + rand(-32, 32);
            return {
                left: rand(c.left[0], c.left[1]),
                top: rand(c.top[0], c.top[1]),
                angle,
                corner: true,
            };
        }

        const mode = Math.random();
        if (mode < 0.28) {
            return {
                left: rand(-4, 104),
                top: rand(-6, -1),
                angle: rand(-75, 75),
                corner: false,
            };
        }
        if (mode < 0.56) {
            return {
                left: rand(101, 106),
                top: rand(0, 100),
                angle: rand(95, 265),
                corner: false,
            };
        }
        if (mode < 0.72) {
            return {
                left: rand(-6, -1),
                top: rand(0, 100),
                angle: rand(-85, 85),
                corner: false,
            };
        }
        if (mode < 0.86) {
            return {
                left: rand(0, 100),
                top: rand(101, 106),
                angle: rand(75, 285),
                corner: false,
            };
        }
        return {
            left: rand(8, 92),
            top: rand(10, 88),
            angle: rand(0, 360),
            corner: false,
        };
    }

    function spawnShard(fragments, field, reduced) {
        const origin = spawnOrigin();
        const el = document.createElement("span");
        el.className = "shard shard--" + pick(PALETTE);
        if (origin.corner) el.classList.add("shard--corner");

        let text = pick(fragments);
        if (Math.random() < 0.18) text = text.split("").reverse().join("");
        if (Math.random() < 0.12) text = text.toUpperCase();
        el.textContent = text;

        const dist = origin.corner ? rand(55, 165) : rand(35, 130);
        const rad = (origin.angle * Math.PI) / 180;
        const dx = Math.cos(rad) * dist;
        const dy = Math.sin(rad) * dist;
        const rot0 = origin.angle + rand(-18, 18);
        const rot1 = rot0 + rand(-55, 55);
        const dur = origin.corner ? rand(5, 16) : rand(7, 24);

        el.style.left = origin.left + "%";
        el.style.top = origin.top + "%";
        el.style.setProperty("--dx", dx + "vmin");
        el.style.setProperty("--dy", dy + "vmin");
        el.style.setProperty("--rot0", rot0 + "deg");
        el.style.setProperty("--rot1", rot1 + "deg");
        el.style.setProperty("--op", String(rand(0.45, 0.92)));
        el.style.animationDuration = dur + "s";
        if (Math.random() < 0.22) el.style.fontSize = rand(0.62, 1.05) + "rem";

        field.appendChild(el);
        el.addEventListener("animationend", () => el.remove(), { once: true });
        if (!reduced) {
            const cap = window.innerWidth < 640 ? 36 : 62;
            if (field.childElementCount > cap) field.firstElementChild?.remove();
        }
    }

    function init() {
        const field = document.getElementById("campus-chaos");
        if (!field) return;

        const reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
        const fragments = collectFragments();

        if (reduced) {
            for (let i = 0; i < 6; i++) {
                const el = document.createElement("span");
                el.className = "shard shard--static shard--" + pick(PALETTE);
                el.textContent = pick(fragments);
                el.style.left = rand(5, 85) + "%";
                el.style.top = rand(12, 78) + "%";
                el.style.setProperty("--rot0", rand(-40, 40) + "deg");
                field.appendChild(el);
            }
            return;
        }

        const burst = 10;
        for (let i = 0; i < burst; i++) {
            setTimeout(() => spawnShard(fragments, field, reduced), i * rand(60, 180));
        }

        function pulse() {
            spawnShard(fragments, field, reduced);
            if (Math.random() < 0.35) {
                setTimeout(() => spawnShard(fragments, field, reduced), rand(40, 220));
            }
            setTimeout(pulse, rand(120, 780));
        }
        pulse();
    }

    function initWarpTrace() {
        const canvas = document.getElementById("warp-trace");
        if (!canvas || window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
            return;
        }
        const ctx = canvas.getContext("2d");
        if (!ctx) return;

        let w = 0;
        let h = 0;
        const trails = [];
        const hues = [275, 295, 320, 168, 350];

        function resize() {
            w = canvas.width = window.innerWidth;
            h = canvas.height = window.innerHeight;
        }

        function spawn(fromEdge) {
            let x;
            let y;
            let angle;
            if (fromEdge && Math.random() < 0.55) {
                const edge = Math.floor(Math.random() * 4);
                if (edge === 0) {
                    x = rand(-40, w * 0.15);
                    y = rand(0, h);
                    angle = rand(-35, 35);
                } else if (edge === 1) {
                    x = rand(w * 0.85, w + 40);
                    y = rand(0, h);
                    angle = rand(145, 215);
                } else if (edge === 2) {
                    x = rand(0, w);
                    y = rand(-40, h * 0.12);
                    angle = rand(55, 125);
                } else {
                    x = rand(0, w);
                    y = rand(h * 0.88, h + 40);
                    angle = rand(-125, -55);
                }
            } else {
                x = rand(0, w);
                y = rand(0, h);
                angle = rand(0, 360);
            }
            trails.push({
                x,
                y,
                angle,
                len: rand(90, 320),
                speed: rand(0.35, 1.4),
                hue: pick(hues),
                life: rand(0.55, 1),
                decay: rand(0.004, 0.014),
                width: rand(1.2, 4.5),
                curl: rand(-0.02, 0.02),
            });
        }

        function frame() {
            ctx.fillStyle = "rgba(10, 1, 20, 0.11)";
            ctx.fillRect(0, 0, w, h);

            for (const t of trails) {
                const rad = (t.angle * Math.PI) / 180;
                const ex = t.x + Math.cos(rad) * t.len;
                const ey = t.y + Math.sin(rad) * t.len;
                const g = ctx.createLinearGradient(t.x, t.y, ex, ey);
                const a = 0.32 * t.life;
                g.addColorStop(0, `hsla(${t.hue}, 92%, 62%, 0)`);
                g.addColorStop(0.35, `hsla(${t.hue}, 92%, 68%, ${a})`);
                g.addColorStop(0.7, `hsla(${t.hue + 20}, 88%, 58%, ${a * 0.6})`);
                g.addColorStop(1, `hsla(${t.hue}, 92%, 62%, 0)`);
                ctx.strokeStyle = g;
                ctx.lineWidth = t.width;
                ctx.lineCap = "round";
                ctx.beginPath();
                ctx.moveTo(t.x, t.y);
                ctx.lineTo(ex, ey);
                ctx.stroke();

                t.x += Math.cos(rad) * t.speed;
                t.y += Math.sin(rad) * t.speed;
                t.angle += t.curl * 57;
                t.life -= t.decay;
            }

            for (let i = trails.length - 1; i >= 0; i--) {
                if (trails[i].life <= 0) trails.splice(i, 1);
            }
            if (trails.length < 28 && Math.random() < 0.18) spawn(true);
            if (Math.random() < 0.06) spawn(false);
            requestAnimationFrame(frame);
        }

        resize();
        window.addEventListener("resize", resize);
        for (let i = 0; i < 12; i++) spawn(true);
        requestAnimationFrame(frame);
    }

    function boot() {
        init();
        initWarpTrace();
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", boot);
    } else {
        boot();
    }
})();
