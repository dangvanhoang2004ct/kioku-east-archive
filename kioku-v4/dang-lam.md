# KIOKU — Việc đang làm

## Checkpoint xác minh: 16/11/2026 — KIOKU V6 / Shelf Echo
- [x] GitHub riêng: `dangvanhoang2004ct/kioku-east-archive`; dự án website ở `kioku-v4/`.
- [x] PR #1 "KIOKU V6 — Shelf Echo redesign and collector UX" đã merge vào `main`; merge SHA **`d8299feb3813941200bb036be417785c31069f0f`** (đối chiếu GitHub).
- [x] README V6 công bố 7 trang tiếng Anh: Home, Collection, Finder, line Reference Detail, Condition Guide, Journal, About.
- [x] V6 có Search, Filters/Sort, Saved References, Compare (tối đa 3), Finder, Zoom và Local Condition Notes copy/export trong mã/README.
- [x] Theo báo cáo Codex/người dùng: Cloudflare Production `https://kioku-east-archive.pages.dev/`, Preview `https://07e5f658.kioku-east-archive.pages.dev/`; 7 trang Production HTTP 200 và tài nguyên khớp Preview QA.
- [x] Theo mô tả PR #1: `npm run build`; Chromium + WebKit tại 320/375/390/768/1440 PASS. **Các kết quả này từ báo cáo PR/Codex, không phải phép đo lại trong phiên cập nhật tài liệu.**
- [ ] Trực tiếp xác nhận trạng thái Cloudflare runtime mới nhất khi có yêu cầu vận hành/triển khai; một GitHub merge không tự chứng minh Production.
- [ ] Đồng bộ và rà soát bản `chatgpt.md`, `design-rule.md`, `dang-lam.md` trên Mac nếu chúng mới hơn tài liệu GitHub. Không chép bản V4 cũ đè V6.

## Việc ưu tiên
- [ ] Rà soát PR tài liệu V6 này rồi merge riêng; chỉ cập nhật docs, không thay build hoặc mã Production.
- [ ] Bổ sung danh mục tồn kho thật (Bandai Spirits/MegaHouse): ảnh đúng món và quyền dùng, SKU, tình trạng figure/box, phụ kiện/lỗi, giá, số lượng, xuất xứ gửi hàng.
- [ ] Chỉ phát triển checkout/thanh toán/vận chuyển khi có dữ liệu, chính sách và backend xác thực; không nhầm reference catalogue với active stock.
- [ ] Nếu làm UI tiếp, bắt đầu từ Shelf Echo V6; branch → Cloudflare Preview → duyệt rồi mới lên Production.

## Ranh giới
Chỉ sửa repository Kioku. Không ghi đè mã, quy tắc, tài sản hoặc cấu hình Cloudflare của Momo Matcha. Tài liệu nguồn trong môi trường chat có bản V4 cũ; checkpoint V6 là bằng chứng GitHub/PR mới nhất.
