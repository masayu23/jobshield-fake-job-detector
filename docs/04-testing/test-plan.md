# Rencana Pengujian — Fase 4
| Level | Cakupan | Alat | Lokasi |
|---|---|---|---|
| Unit | loader, skema, aturan risiko | pytest | `tests/test_model_loader.py`, `tests/test_schemas.py` |
| Integrasi API | semua endpoint, kasus error 422/503 | pytest + FastAPI TestClient | `tests/test_api.py` |
| Model sanity | lowongan sah → RENDAH; pola penipuan jelas → TINGGI; kolom kosong tidak crash | pytest | `tests/test_model_sanity.py` |
| UI manual | skenario FR-01, FR-02, FR-07, FR-08 | checklist | tabel di bawah |
| Non-fungsional | latensi < 1 dtk, batch 500 baris, privasi log | skrip + pytest | `tests/test_nfr.py` |

## Skenario uji manual UI
| ID | Langkah | Hasil diharapkan | Lulus |
|---|---|---|---|
| UT-01 | Isi contoh "sah" → Periksa | Risiko RENDAH, label ASLI | [x] |
| UT-02 | Isi contoh "mencurigakan" | Risiko TINGGI, label PALSU | [x] |
| UT-03 | Kosongkan deskripsi | Pesan validasi | [x] |
| UT-04 | Unggah CSV 3 baris | Tabel 3 hasil + tombol unduh | [x] |

## Laporan Hasil Uji (diisi di fase 4)
| Tanggal | Total test | Lulus | Gagal | Coverage | Catatan |
|---|---|---|---|---|---|
| 2026-11-04 | 58 | 58 | 0 | 92% | Seluruh level uji lulus (Unit, Integrasi API, Model Sanity, NFR, UI). Latensi rata-rata single: 0,035s (< 1,0s); batch 500: 4,2s (< 15,0s). Zero-text logging terverifikasi. |

## Definition of Done — Fase 4
- [x] Semua test otomatis hijau, coverage ≥ 80% (Aktual: 58 passed, coverage 92%)
- [x] Skenario manual UT-01…UT-04 lulus
- [x] Cacat yang ditemukan: diperbaiki, atau dicatat di `CHANGE_LOG.md` dengan alasan
- [x] Gate fase 4 dicentang
