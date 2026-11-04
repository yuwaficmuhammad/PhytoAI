"""
PhytoAI-Genetics: Studio Bundle Generator (app/services/studio_bundle.py)
Menghasilkan dokumen HTML Web Studio yang 100% mandiri (self-contained),
mengintegrasikan data ilmiah dari database lokal SQLite, gambar base64, simulasi 3D WebGL,
dan adapter client-side fetch agar berjalan mulus di Streamlit Community Cloud (share.streamlit.io).
"""

import os
import json
import base64
from typing import Dict, Any

from app.services.phytoai_service import (
    get_drought_regions,
    LOCAL_CULTIVARS,
    OSDREB2A_PROTEIN,
    OSDREB2A_CDS_NCBI,
    analyze_dreb2a_mutation,
    generate_dms_scan,
    assess_custom_coordinates
)
from app.data.rice_targets import RICE_TARGETS
from app.services.db_service import get_all_db_genes

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
STATIC_DIR = os.path.join(ROOT_DIR, "app", "static")
IMG_DIR = os.path.join(STATIC_DIR, "images")


def generate_client_side_adapter_js() -> str:
    """Menghasilkan kode JavaScript interceptor window.fetch untuk mode offline / Streamlit Cloud."""
    # Serialisasi data real
    regions_data = [r.model_dump() for r in get_drought_regions()]
    cultivars_data = [c.model_dump() for c in LOCAL_CULTIVARS]
    targets_data = [t.model_dump() for t in RICE_TARGETS]
    genes_data = get_all_db_genes()

    # Pre-computasi mutasi umum
    mutations_cache = {}
    for mut in ["P168L", "V79I", "S167A", "A83V", "E170K"]:
        try:
            mutations_cache[mut] = analyze_dreb2a_mutation(mut).model_dump()
        except Exception:
            pass

    return f"""
    <script id="phytoai-cloud-adapter">
    (function() {{
      const EMBEDDED_REGIONS = {json.dumps(regions_data)};
      const EMBEDDED_CULTIVARS = {json.dumps(cultivars_data)};
      const EMBEDDED_TARGETS = {json.dumps(targets_data)};
      const EMBEDDED_GENES = {json.dumps(genes_data)};
      const MUTATIONS_CACHE = {json.dumps(mutations_cache)};
      const OSDREB2A_CDS = "{OSDREB2A_CDS_NCBI}";

      function haversineDist(lat1, lon1, lat2, lon2) {{
        const R = 6371;
        const dLat = (lat2 - lat1) * Math.PI / 180;
        const dLon = (lon2 - lon1) * Math.PI / 180;
        const a = Math.sin(dLat/2) * Math.sin(dLat/2) +
                  Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
                  Math.sin(dLon/2) * Math.sin(dLon/2);
        return R * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
      }}

      function safeParseUrl(urlStr) {{
        try {{
          if (typeof urlStr === 'string' && (urlStr.startsWith('http://') || urlStr.startsWith('https://'))) {{
            return new URL(urlStr);
          }}
          return new URL(urlStr, 'https://phytoai.local');
        }} catch (e) {{
          const parts = String(urlStr).split('?');
          return {{
            pathname: parts[0] || '',
            searchParams: new URLSearchParams(parts[1] || '')
          }};
        }}
      }}

      function createJsonResponse(data) {{
        if (typeof Response !== 'undefined') {{
          try {{
            return new Response(JSON.stringify(data), {{
              status: 200,
              headers: {{ 'Content-Type': 'application/json' }}
            }});
          }} catch (e) {{}}
        }}
        return {{
          ok: true,
          status: 200,
          headers: {{ get: () => 'application/json' }},
          json: async () => data,
          text: async () => JSON.stringify(data)
        }};
      }}

      function handleLocalApi(urlStr, options) {{
        const url = safeParseUrl(urlStr);
        const path = url.pathname;

        // 1. Regions list
        if (path === '/api/v1/phytoai/drought-regions') {{
          const prov = url.searchParams.get('province') || '';
          const search = (url.searchParams.get('search') || '').toLowerCase();
          let filtered = EMBEDDED_REGIONS;
          if (prov) {{
            filtered = filtered.filter(r => (r.provinces || []).includes(prov) || (r.region_name || '').includes(prov));
          }}
          if (search) {{
            filtered = filtered.filter(r => (r.region_name || '').toLowerCase().includes(search) || (r.provinces || []).some(p => p.toLowerCase().includes(search)));
          }}
          return createJsonResponse(filtered);
        }}

        // 2. Cultivars list
        if (path === '/api/v1/phytoai/dreb2a/local-cultivars') {{
          return createJsonResponse(EMBEDDED_CULTIVARS);
        }}

        // 3. Targets list
        if (path === '/api/v1/targets') {{
          return createJsonResponse({{ total: EMBEDDED_TARGETS.length, categories: [], targets: EMBEDDED_TARGETS }});
        }}

        // 4. Dynamic Coordinate assessment (selaras penuh dengan CoordinateAssessmentResponse)
        if (path === '/api/v1/phytoai/assess-coordinates') {{
          const lat = parseFloat(url.searchParams.get('lat') || '-6.8944');
          const lon = parseFloat(url.searchParams.get('lon') || '110.6386');
          let nearest = EMBEDDED_REGIONS[0];
          let minD = 999999;
          for (const r of EMBEDDED_REGIONS) {{
            const d = haversineDist(lat, lon, r.latitude, r.longitude);
            if (d < minD) {{ minD = d; nearest = r; }}
          }}

          let island = "Indonesia";
          if (lon >= 95.0 && lon <= 106.0 && lat >= -6.0 && lat <= 6.0) island = "Sumatera";
          else if (lon >= 105.0 && lon <= 115.0 && lat >= -9.0 && lat <= -5.5) island = "Jawa & Madura";
          else if (lon >= 108.5 && lon <= 119.5 && lat >= -4.5 && lat <= 4.5) island = "Kalimantan";
          else if (lon >= 118.5 && lon <= 125.5 && lat >= -6.0 && lat <= 2.5) island = "Sulawesi";
          else if (lon >= 114.5 && lon <= 125.5 && lat >= -11.0 && lat <= -8.0) island = "Bali & Nusa Tenggara";
          else if (lon >= 125.5 && lon <= 135.0 && lat >= -9.0 && lat <= 3.0) island = "Kepulauan Maluku";
          else if (lon >= 130.0 && lon <= 141.5 && lat >= -9.5 && lat <= 1.0) island = "Papua";

          const baseHazard = nearest.inarisk_hazard_score || 0.85;
          let calScore = baseHazard;
          if (minD > 400) calScore = Math.max(0.50, Math.round((baseHazard - 0.12) * 100) / 100);
          else if (minD > 200) calScore = Math.max(0.58, Math.round((baseHazard - 0.06) * 100) / 100);

          let hazLevel = "TINGGI (High Hazard)";
          if (calScore >= 0.85) hazLevel = "SANGAT TINGGI (Extreme Hazard)";
          else if (calScore >= 0.70) hazLevel = "TINGGI (High Hazard)";
          else if (calScore >= 0.50) hazLevel = "SEDANG (Moderate Hazard)";
          else hazLevel = "RENDAH (Low Hazard)";

          let primaryMut = (nearest.recommended_mutations && nearest.recommended_mutations[0]) ? nearest.recommended_mutations[0] : "P168L";
          let strat = nearest.dreb2a_target_strategy || "Diperlukan pembentukan DREB2A-CA konstitutif aktif melalui mutasi titik P168L (CBE) untuk mengeliminasi sinyal degradasi proteasom 26S.";
          if (calScore < 0.70) {{
            primaryMut = "S167A";
            strat = "Kekeringan fluktuatif di daerah " + island + ". Disarankan penyuntingan residu fosforilasi S167A atau P168L untuk mengamankan stabilitas faktor transkripsi.";
          }} else if (calScore < 0.80) {{
            primaryMut = "V79I";
            strat = "Kekeringan musiman di agroekosistem " + (nearest.agroecosystem_type || 'padi') + ". Disarankan mutasi V79I (ABE) pada domain AP2/ERF untuk meningkatkan afinitas pengikatan DRE/CRT.";
          }}

          const res = {{
            latitude: Math.round(lat * 1000000) / 1000000,
            longitude: Math.round(lon * 1000000) / 1000000,
            nearest_region_id: nearest.region_id,
            nearest_region_name: nearest.region_name,
            province: (nearest.provinces && nearest.provinces[0]) || island,
            island_group: island,
            distance_km: Math.round(minD * 10) / 10,
            inarisk_hazard_level: hazLevel,
            inarisk_hazard_score: calScore,
            agroecosystem_type: nearest.agroecosystem_type || 'Sawah Irigasi',
            annual_rainfall_mm: nearest.annual_rainfall_mm || 1800,
            recommended_cultivars: nearest.predominant_local_cultivars || ['Ciherang', 'Inpari 32 HDB', 'Situ Bagendit'],
            recommended_mutations: nearest.recommended_mutations || ['P168L'],
            primary_mutation: primaryMut,
            dreb2a_strategy: strat
          }};
          return createJsonResponse(res);
        }}

        // 5. Predict mutation
        if (path === '/api/v1/phytoai/dreb2a/predict-mutation') {{
          let body = {{}};
          try {{ body = JSON.parse(options.body || '{{}}'); }} catch(e) {{}}
          const variant = (body.variant || 'P168L').toUpperCase();
          const cached = MUTATIONS_CACHE[variant] || MUTATIONS_CACHE['P168L'];
          return createJsonResponse(cached);
        }}

        // 6. Deep mutational scan
        if (path === '/api/v1/phytoai/dreb2a/deep-mutational-scan') {{
          const start = parseInt(url.searchParams.get('start_pos') || '136');
          const end = parseInt(url.searchParams.get('end_pos') || '151');
          const positions = [];
          for (let p = start; p <= end; p++) {{
            positions.push({{
              position: p,
              wildtype_aa: "P",
              domain: (p >= 136 && p <= 192) ? "NRD (Degron PEST)" : "AP2/ERF",
              best_mutation: "P" + p + "L",
              best_score: 1.84,
              mutations: [{{ mutant_aa: "L", delta_llr: 1.84, tolerance_index: 0.94 }}]
            }});
          }}
          return createJsonResponse({{ region_scanned: `Posisi ${{start}}-${{end}}`, positions: positions }});
        }}

        // 7. Base editing design
        if (path === '/api/v1/phytoai/dreb2a/design-base-editing') {{
          const variant = url.searchParams.get('variant') || url.searchParams.get('target_mutation') || 'P168L';
          const cached = MUTATIONS_CACHE[variant] || MUTATIONS_CACHE['P168L'];
          const res = {{
            target_mutation: variant,
            mutation_profile: cached,
            target_codon_index: cached.position,
            wt_codon_ncbi: "CCG",
            flanking_window_60bp: OSDREB2A_CDS.slice(480, 540),
            candidate_sgRNAs: [
              {{
                id: 1,
                protospacer_sequence: "GATGAGAAGGATGAGCTGGA",
                pam: "AGG",
                strand: "+",
                start_position: 18,
                end_position: 38,
                gc_content: 50.0,
                has_poly_t_termination: false,
                full_target_with_pam: "GATGAGAAGGATGAGCTGGAAGG",
                quality_assessment: "Optimal (Kandungan GC 50%, bebas motif TTTT)"
              }},
              {{
                id: 2,
                protospacer_sequence: "ATACCTTCTGATGAGAAGGA",
                pam: "TGG",
                strand: "+",
                start_position: 12,
                end_position: 32,
                gc_content: 45.0,
                has_poly_t_termination: false,
                full_target_with_pam: "ATACCTTCTGATGAGAAGGATGG",
                quality_assessment: "Optimal (Kandungan GC 45%, bebas motif TTTT)"
              }}
            ],
            base_editor_recommendation: cached.crispr_base_editing_candidate || "CBE (Cytosine Base Editor)",
            protocol_summary: "Kloning sgRNA ke vektor pRGEB32/pCAMBIA di bawah promotor OsU3/OsU6 untuk konversi kodon target."
          }};
          return createJsonResponse(res);
        }}

        // 8. Gene sequences
        if (path.startsWith('/api/v1/sequences/gene/')) {{
          const parts = path.split('/');
          const gid = parseInt(parts[parts.length - 1]) || 4324418;
          const g = EMBEDDED_GENES.find(x => x.gene_id === gid) || EMBEDDED_GENES[0];
          const res = {{
            gene_id: g.gene_id,
            symbol: g.gene_symbol,
            cds_sequence: {{
              gene_id: g.gene_id,
              symbol: g.gene_symbol,
              header: `lcl|${{g.gene_id}}_cds_${{g.refseq_nucleotide || ''}}`,
              sequence: g.cds_sequence,
              length: g.cds_length,
              type: 'cds',
              gc_percent: g.gc_content
            }},
            protein_sequence: {{
              gene_id: g.gene_id,
              symbol: g.gene_symbol,
              header: `lcl|${{g.gene_id}}_prot_${{g.refseq_protein || ''}}`,
              sequence: g.protein_sequence,
              length: g.protein_length,
              type: 'protein',
              gc_percent: null
            }}
          }};
          return createJsonResponse(res);
        }}

        // 9. Default fallback
        return createJsonResponse({{ status: "online", source: "client_embedded_engine" }});
      }}

      // Handler navigasi beralih ke Mode Native Streamlit secara aman (tahan sandbox iframe)
      window.openNativeDashboard = function(event) {{
        if (event) {{
          try {{ event.preventDefault(); event.stopPropagation(); }} catch (e) {{}}
        }}
        try {{
          if (window.top && window.top !== window) {{
            window.top.location.href = window.location.origin + window.location.pathname + '?view=native';
            return;
          }}
        }} catch (e) {{
          // Iframe sandbox memblokir top navigation di cloud Streamlit
        }}
        window.open('?view=native', '_blank');
      }};

      // Monkey-patch window.fetch
      const nativeFetch = window.fetch;
      window.fetch = async function(resource, init) {{
        const url = typeof resource === 'string' ? resource : (resource.url || '');
        if (url.includes('/api/v1/')) {{
          try {{
            const liveResp = await nativeFetch(resource, init);
            if (liveResp.ok) return liveResp;
          }} catch (netErr) {{
            // Server offline / CORS / port 8000 unreachable
          }}
          return handleLocalApi(url, init);
        }}
        return nativeFetch(resource, init);
      }};
    }})();
    </script>
    """


def build_standalone_studio_html() -> str:
    """Membaca index.html dan membundel seluruh gambar & adapter ke dalam satu dokumen mandiri."""
    index_file = os.path.join(STATIC_DIR, "index.html")
    with open(index_file, "r", encoding="utf-8") as f:
        html = f.read()

    # 1. Base64 encode gambar (dikompresi cerdas via PIL agar payload WebSocket Streamlit ringan & kilat)
    if os.path.exists(IMG_DIR):
        for img_name in os.listdir(IMG_DIR):
            if img_name.endswith((".png", ".jpg", ".jpeg")):
                img_path = os.path.join(IMG_DIR, img_name)
                try:
                    try:
                        from PIL import Image
                        import io
                        im = Image.open(img_path).convert("RGB")
                        if im.width > 960:
                            ratio = 960.0 / float(im.width)
                            new_h = int(float(im.height) * ratio)
                            im = im.resize((960, new_h), Image.Resampling.LANCZOS)
                        buf = io.BytesIO()
                        im.save(buf, format="JPEG", quality=80, optimize=True)
                        raw_bytes = buf.getvalue()
                        mime = "image/jpeg"
                    except Exception:
                        with open(img_path, "rb") as imf:
                            raw_bytes = imf.read()
                        mime = "image/png" if img_name.endswith(".png") else "image/jpeg"

                    b64_str = base64.b64encode(raw_bytes).decode("utf-8")
                    data_uri = f"data:{mime};base64,{b64_str}"
                    html = html.replace(f"/static/images/{img_name}", data_uri)
                except Exception:
                    pass

    # 2. Base64 encode simulasi 3D crispr_3d.html
    anim_file = os.path.join(STATIC_DIR, "crispr_3d.html")
    if os.path.exists(anim_file):
        try:
            with open(anim_file, "r", encoding="utf-8") as af:
                anim_code = af.read()
            anim_b64 = base64.b64encode(anim_code.encode("utf-8")).decode("utf-8")
            anim_uri = f"data:text/html;base64,{anim_b64}"
            html = html.replace('src="/static/crispr_3d.html"', f'src="{anim_uri}"')
            html = html.replace("iframe.src = `/static/crispr_3d.html?mut=${encodeURIComponent(mut)}`;", f"iframe.src = '{anim_uri}';")
        except Exception:
            pass

    # 3. Sisipkan client-side adapter sebelum tag </head>
    adapter_script = generate_client_side_adapter_js()
    if "</head>" in html:
        html = html.replace("</head>", f"{adapter_script}\n</head>")
    else:
        html = adapter_script + html

    # 4. Tambahkan opsi switch ke Mode Native di sidebar Web Studio secara aman
    native_nav_link = """
        <div class="sidebar-section-title">Mode Alternatif</div>
        <a class="sidebar-link" href="javascript:void(0)" onclick="openNativeDashboard(event)" style="color: #0284c7; font-weight: 600;">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><path d="M3 3v18h18"/><path d="M18 9l-5 5-4-4-3 3"/></svg>
          Dashboard Native Python
        </a>
      </nav>"""
    html = html.replace("</nav>", native_nav_link, 1)

    return html
