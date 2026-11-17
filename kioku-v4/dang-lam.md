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
- [x] PR #3 commit `f488ca1028d355b2d741f452b11ab8ef5b21da53`: kiểm tra tĩnh tính nhất quán 10/10 PASS, Cloudflare Pages check báo Preview deploy success tại `https://a9bceeda.kioku-east-archive.pages.dev/`. Hai PR #2 (tài liệu) và #3 (giao diện) đã chuyển sang Ready for review; **chưa merge**.
- [ ] Chưa thực hiện QA trình duyệt Safari/WebKit/Chromium thực tế cho commit mới; phải kiểm tra các thao tác ảnh 3D/fallback và URL Production khi phát hành.
- [ ] Khi phát hành: merge PR #2 và PR #3 theo thứ tự an toàn, xác nhận Cloudflare Pages Production nhận đúng commit, không đụng Momo/RoleFit.

## Artwork của chủ dự án — 17/11/2026
- [x] Người dùng gửi sheet logo KIOKU với rồng xanh quấn xuyên chữ và xác nhận đây là hình rồng phải xuất hiện trực tiếp trên website, **không chỉ mesh 3D**.
- [x] Đã tạo asset SVG vector hóa từ đường nét của ảnh gốc (mẫu logo trung tâm trong sheet): `assets/img/kioku-owner-dragon-logo.svg`, thêm vào trang Home và quy trình build trên PR #3. Đây là bản truy nét đơn giản hóa, không phải bản PNG gốc đầy đủ gradient.
- [x] Tầng WebGL 3D vẫn giữ và chuyển động phía sau; logo/rồng minh họa nằm phía trước trên nền giấy sáng để giữ tương phản chữ navy, trang vẫn theo nhận diện midnight/lavender.
- [ ] Xác minh Cloudflare Preview/Production và thiết bị thật sau merge; không nhận rằng asset mới là mô hình 3D có khớp hình minh họa 1:1.

## Khắc phục lỗi hiển thị rồng 3D — 17/11/2026
- [x] Đã xác định hồi quy: thẻ `hero-owner-art` cao ~1.100px ở giữa sân khấu với nền giấy sáng che WebGL, trong khi `.hero-dragon` bị giảm opacity 0.35/0.28. Đây là lỗi layer/CSS, không đủ bằng chứng để kết luận hỏng mô hình 3D.
- [x] PR #4: di chuyển logo rồng của chủ thương hiệu xuống phần giới thiệu **bên dưới** sân khấu, bật rồng WebGL opacity 1, gỡ CSS ẩn fallback ở reduced-motion, chỉ đánh dấu canvas sẵn sàng sau frame vẽ không lỗi; bổ sung assertion chống hồi quy.
- [x] Cloudflare Preview PR #4 tại `https://972beb48.kioku-east-archive.pages.dev/` cho commit `63a801eb` báo deploy SUCCESS. Chromium layout fixture ở 320/375/390/768/1440 không đè hình 3D, không horizontal overflow.
- [ ] Môi trường browser hiện không cung cấp WebGL/GPU và không truy cập Cloudflare URL trực tiếp để đo render thật; **không tuyên bố hoạt ảnh 3D đã được kiểm tra trực quan trên Safari/Chromium thực tế**.
- [ ] Sau merge xác minh Cloudflare Production check khớp SHA; nếu trình duyệt người dùng vẫn không hỗ trợ WebGL thì fallback SVG phải hiện rõ.

## Quyết định đính chính — một rồng duy nhất có chuyển động 3D (17/11/2026)
- [x] Người dùng xác nhận lần trước **sai ý**: không được để con rồng WebGL hình khối và hình rồng minh họa tách thành 2. Rồng minh họa từ logo xanh KIOKU phải là bề mặt chuyển động của **chính mô hình WebGL**.
- [x] Trên branch `feature/kioku-textured-dragon-webgl-20261117`: tách 3 asset từ SVG truy nét của artwork chủ thương hiệu (`kioku-owner-dragon-surface.svg`, `kioku-owner-wordmark-only.svg`, `kioku-owner-logo-stage-still.svg`). Không tạo ảnh AI mới, không thêm framework.
- [x] Thay `features/shared/dragon-scene.js` bằng một lưới tam giác WebGL có texture rồng thật từ asset, uốn dọc thân và biến dạng theo chiều sâu; chuyển động chịu ảnh hưởng rất nhẹ bởi con trỏ. Đầu chuyển động ít hơn đuôi. Xóa mesh rồng hình khối thứ hai.
- [x] Trang Home xóa `hero-owner-art` trong phần giới thiệu; chữ KIOKU đứng yên phía sau **cùng** canvas WebGL, rồng minh họa chuyển động phía trước. Dự phòng tĩnh khi WebGL không khả dụng hoặc `prefers-reduced-motion`.
- [ ] Phân biệt rõ WebGL textured surface / 2.5D với mô hình rồng 3D khối hoàn chỉnh/rigged: đây là lưới 3D bề mặt, không khẳng định full volume rig.
- [ ] QA khả năng dựng WebGL thật trên GPU Safari/Chromium trước khi tuyên bố hoạt ảnh PASS. Hệ thống Chromium cục bộ có thể chạy nhưng WebGL context bị chặn; kiểm tra cú pháp, tài nguyên và Cloudflare build riêng.
- [ ] Cloudflare Production chỉ có thể xác nhận khi đúng commit trên `main` và check deploy success; giữ Production an toàn khi Preview chưa được nghiệm thu GPU.

### Checkpoint triển khai Preview — 17/11/2026
- [x] PR #5 từ `feature/kioku-textured-dragon-webgl-20261117` đã tạo, kiểm tra tĩnh 11/11 bất biến về một rồng, chuyển động mesh, texture, asset build và fallback đạt yêu cầu.
- [x] Cloudflare Pages báo Preview deploy SUCCESS cho SHA `1088b11ef9c9dab72ca7a5f61ff84fd46dc3e9ba`, URL `https://0ba23fdc.kioku-east-archive.pages.dev/`.
- [ ] **Chưa merge vào main/Production.** Chưa xác minh GPU WebGL thực tế trên Safari/Chromium; browser trong môi trường hiện tại không cấp WebGL context. Cần kiểm tra chuyển động với trình duyệt có WebGL trước khi phát hành, không chỉ dựa vào deploy success.

- [x] Nâng chất lượng mô hình sau checkpoint: tách texture WebP có alpha trực tiếp từ bản cắt của artwork chủ thương hiệu trước đó, giữ chi tiết màu xanh/thân và đầu; upload nhị phân vào repo tại `assets/img/kioku-owner-dragon-texture.webp`, chuyển WebGL sang dùng texture này. Bản SVG truy nét đơn giản chỉ còn là tài nguyên dự phòng/đối chiếu. Không vẽ thêm hình AI.
