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

## UI Preview checkpoint — 17/11/2026
- [x] Người dùng duyệt hướng tham chiếu mới: KIOKU nền tối, sắc tím trang nhã; thanh điều hướng và sân khấu Home tràn bề ngang desktop; hình rồng là điểm nhấn chuyển động 3D; phần giới thiệu và CTA nằm **bên dưới** sân khấu thay vì cạnh hình.
- [x] PR #3 (Preview only) đã chuyển thành full-bleed dark hero và renderer WebGL nguyên bản; head SHA `560c34643fb095e9925c8a4f2b4bc4fbb9494249`.
- [x] GitHub Check Run `Cloudflare Pages` báo **deploy Preview success**, URL `https://3c9b404e.kioku-east-archive.pages.dev/` với SHA `560c346`. JavaScript renderer được đối chiếu cú pháp qua trình phân tích JS.
- [ ] Chưa nghiệm thu tương tác và khung hình WebGL trên Safari/Chromium thực tế; chưa gọi QA browser PASS.
- [ ] Chưa merge PR #3 hoặc thay Production; chờ chủ dự án xem Preview và xác nhận.
- [ ] Điều chỉnh bản 3D nếu hình khối chưa truyền đạt đúng linh vật theo ý chủ thương hiệu, tránh thay logo Shelf Echo.

## Quyết định duyệt rồng KIOKU — 17/11/2026
- [x] Người dùng **chấp nhận hình dáng rồng 3D và chuyển động tổng thể** của bản Preview PR #3; giữ nguyên silhouette, form, phối màu và bố cục sân khấu.
- [x] Yêu cầu tinh chỉnh đã được đưa vào `features/shared/dragon-scene.js` trên PR #3: sóng uốn lượn lan từ phần trước về đuôi, biên độ tăng dần về phía đuôi, phần đầu ổn định, độ biến dạng nhỏ; giữ sửa pháp tuyến để ánh sáng đúng với hình khối và hỗ trợ `prefers-reduced-motion`.
- [x] Hero và header sử dụng asset nhận diện Shelf Echo **`brand/kioku-lockup-light.svg`** gốc, build copy asset vào `dist`; không tự tạo logo mới.
- [x] ChatGPT chỉnh mã nguồn trực tiếp trên PR #3, ghi lại quyết định ở nhánh tài liệu PR #2; Codex chỉ còn merge/triển khai Production theo yêu cầu và kiểm chứng.
- [ ] Kiểm chứng build, Preview và thao tác Safari/WebKit/Chromium của commit PR #3 mới trước Production; không đồng nhất push GitHub với site đã cập nhật.
- [ ] Khi phát hành: merge PR #2 và PR #3 theo thứ tự an toàn, xác nhận Cloudflare Pages Production nhận đúng commit, không đụng Momo/RoleFit.
