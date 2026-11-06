# Status Fase Waterfall

Centang gate hanya setelah *Definition of Done* di dokumen fase terpenuhi. Fase berikutnya terkunci sampai gate sebelumnya dicentang.

| # | Fase | Dokumen | Gate lulus | Tanggal | Catatan |
|---|---|---|---|---|---|
| 0 | Model AI (Colab) | `notebooks/`, `models/current/` | [x] | 2026-11-04 | Model terbaik: Logistic Regression, F1 palsu ≈ 0,86 (hold-out) |
| 1 | Requirements | `01-requirements/SRS.md` | [x] | 2026-11-04 | Disetujui pemilik proyek (SRS v1.0, 10 FR, 8 NFR, kontrak model lengkap) |
| 2 | Design | `02-design/` | [x] | 2026-11-04 | Disetujui pemilik proyek (arsitektur, api-spec, ui-design lengkap) |
| 3 | Implementation | `03-implementation/implementation-plan.md` | [x] | 2026-11-04 | Disetujui pemilik proyek (T-01 s.d. T-09 selesai, 41 test hijau, coverage 91%) |
| 4 | Testing | `04-testing/test-plan.md` | [x] | 2026-11-04 | Disetujui pemilik proyek (58 test hijau, coverage 92%, laporan uji lengkap) |
| 5 | Deployment | `05-deployment/deployment-plan.md` | [x] | 2026-11-04 | Disetujui pemilik proyek (Dockerfile non-root, README curl lengkap, tag v1.0.0) |
| 6 | Maintenance | `06-maintenance/maintenance-plan.md` | [ ] | | Prosedur ganti model, skrip swap_model.py, monitoring drift — **fase aktif** |

**Fase aktif saat ini:** 6 (Maintenance)
