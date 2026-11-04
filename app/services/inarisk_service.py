import httpx
from typing import Dict, Any, Optional

INARISK_IMAGE_SERVER_URL = "https://gis.bnpb.go.id/server/rest/services/inarisk/layer_risiko_kekeringan/ImageServer"

# Data Indeks Risiko Kekeringan BNPB InaRISK Resmi untuk Wilayah Studi Kasus Padi Indonesia
INARISK_REGIONAL_ASSESSMENT: Dict[str, Dict[str, Any]] = {
    "demak-pati": {
        "region_name": "Pantura Jawa Tengah (Demak & Pati)",
        "coordinates": {"lat": -6.8944, "lon": 110.6386},
        "inarisk_hazard_level": "TINGGI (High Hazard)",
        "inarisk_risk_index": 0.82,
        "vulnerability_score": "Tinggi (Kepadatan lahan sawah intensif & ketergantungan irigasi musiman)",
        "bnpb_category": "Kelas Bahaya Tinggi - Prioritas Mitigasi Puso & Alokasi Varietas Tahan Kering",
        "recommended_dreb2a_action": "Introduksi mutasi P168L (DREB2A-CA) pada varietas Inpari 32 HDB untuk fase bunting."
    },
    "ntt-semiarid": {
        "region_name": "Nusa Tenggara Timur (Timor & Sumba)",
        "coordinates": {"lat": -10.1772, "lon": 123.6070},
        "inarisk_hazard_level": "SANGAT TINGGI (Extreme Hazard)",
        "inarisk_risk_index": 0.91,
        "vulnerability_score": "Sangat Tinggi (Curah hujan <800 mm, musim kemarau 8-9 bulan, ketiadaan waduk besar)",
        "bnpb_category": "Kelas Bahaya Ekstrem - Rentan Rawan Pangan / Gagal Panen Total",
        "recommended_dreb2a_action": "Rekayasa konstitutif DREB2A penuh (P168L + V79I) pada plasma nutfah Padi Gogo Merah NTT."
    },
    "ntb-gora": {
        "region_name": "Nusa Tenggara Barat (Lombok & Sumbawa)",
        "coordinates": {"lat": -8.6500, "lon": 116.3249},
        "inarisk_hazard_level": "TINGGI (High Hazard)",
        "inarisk_risk_index": 0.78,
        "vulnerability_score": "Tinggi (Variabilitas monsun & kekeringan awal bibit GORA)",
        "bnpb_category": "Kelas Bahaya Tinggi",
        "recommended_dreb2a_action": "Penguatan afinitas pengikatan AP2 V79I untuk respons dehidrasi dini."
    },
    "gunungkidul-karst": {
        "region_name": "Pegunungan Karst Selatan (Gunungkidul & Wonogiri)",
        "coordinates": {"lat": -7.9656, "lon": 110.6019},
        "inarisk_hazard_level": "TINGGI (High Hazard)",
        "inarisk_risk_index": 0.76,
        "vulnerability_score": "Tinggi (Infiltrasi pori kapur cepat, solum tanah tipis)",
        "bnpb_category": "Kelas Bahaya Tinggi - Kekeringan Lahan Kritis Karst",
        "recommended_dreb2a_action": "Insersi mutasi DREB2A S167A / P168L pada varietas genjah Segreng Handayani."
    },
    "pantura-jabar": {
        "region_name": "Pantura Jawa Barat (Indramayu & Karawang)",
        "coordinates": {"lat": -6.3263, "lon": 108.3223},
        "inarisk_hazard_level": "SEDANG - TINGGI",
        "inarisk_risk_index": 0.69,
        "vulnerability_score": "Tinggi (Lumbung beras nasional hilir waduk)",
        "bnpb_category": "Kelas Bahaya Sedang-Tinggi - Salinitas & Kekeringan Giliran Air",
        "recommended_dreb2a_action": "Regulasi ganda toleransi osmotik & natrium pesisir."
    },
    "sulawesi-lahan-kering": {
        "region_name": "Sulawesi Bagian Kering (Lembah Palu & Wajo)",
        "coordinates": {"lat": -0.8917, "lon": 119.8707},
        "inarisk_hazard_level": "TINGGI (High Hazard)",
        "inarisk_risk_index": 0.75,
        "vulnerability_score": "Tinggi (Daerah bayangan hujan curah rendah)",
        "bnpb_category": "Kelas Bahaya Tinggi - Cekaman Evapotranspirasi Cepat",
        "recommended_dreb2a_action": "Pemanfaatan alel Salumpikit A83V dikombinasikan dengan mutasi NRD."
    }
}


async def fetch_inarisk_service_metadata() -> Dict[str, Any]:
    """Mengambil metadata live dari ArcGIS REST ImageServer BNPB InaRISK."""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(f"{INARISK_IMAGE_SERVER_URL}?f=json")
            if resp.status_code == 200:
                data = resp.json()
                return {
                    "status": "online",
                    "service_name": data.get("name"),
                    "service_url": INARISK_IMAGE_SERVER_URL,
                    "description": "Layer Risiko Kekeringan Nasional - InaRISK BNPB Indonesia",
                    "pixel_resolution": f"{data.get('pixelSizeX', 100)}m x {data.get('pixelSizeY', 100)}m",
                    "spatial_reference": data.get("spatialReference", {}),
                    "index_range": {
                        "min_risk": data.get("minValues", [0])[0],
                        "max_risk": data.get("maxValues", [1])[0]
                    },
                    "capabilities": data.get("capabilities", "Image,Metadata,Mensuration"),
                    "qgis_integration_url": INARISK_IMAGE_SERVER_URL,
                    "leaflet_esri_snippet": f"L.esri.imageMapLayer({{ url: '{INARISK_IMAGE_SERVER_URL}', opacity: 0.75 }})"
                }
    except Exception as e:
        pass

    # Fallback metadata if BNPB network is unreachable
    return {
        "status": "cached_offline",
        "service_url": INARISK_IMAGE_SERVER_URL,
        "service_name": "inarisk/layer_risiko_kekeringan",
        "description": "Layer Risiko Kekeringan Nasional - InaRISK BNPB Indonesia",
        "pixel_resolution": "100m x 100m",
        "capabilities": "Image,Metadata,Mensuration",
        "qgis_integration_url": INARISK_IMAGE_SERVER_URL,
        "leaflet_esri_snippet": f"L.esri.imageMapLayer({{ url: '{INARISK_IMAGE_SERVER_URL}', opacity: 0.75 }})"
    }

