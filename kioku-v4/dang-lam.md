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

## Polish sau kiểm tra Preview 390×844 / 1440 — 17/11/2026
- [x] Người dùng đã kiểm tra Preview trước đó: Search, maker filter, Saved, Compare, Finder, condition notes và menu mobile không gặp lỗi chặn. Ghi nhận này là kết quả user QA, không phải thử nghiệm GPU của ChatGPT.
- [x] User phát hiện CTA Collection xuất hiện sau màn hình đầu (vị trí 966px tại 390×844). Đã thêm `hero-mobile-entry` ngay sau sân khấu, giảm chiều cao sân khấu dưới 720px xuống `clamp(310px,42svh,365px)` và bỏ nút Collection trùng trong intro mobile.
- [x] Bổ sung nút Pause/Play thực sự liên kết WebGL; trạng thái `aria-pressed`, disabled khi WebGL không dùng được, `prefers-reduced-motion` giữ ảnh tĩnh. Giữ nguyên một rồng xanh có texture chuyển động và wordmark chung sân khấu.
- [x] Cải thiện hoạt ảnh: tăng độ mịn lưới 88×34 → 112×44, chuyển timer sang delta time có giới hạn khung bị gián đoạn, tăng độ phân giải canvas desktop có kiểm soát và làm dịu tương tác chuột theo thời gian.
- [ ] QA thực tế GPU trên Safari/Chromium mobile và desktop cho nút Pause/Play, giảm chuyển động, viewport 390×844 và 1440px. Static check/Cloudflare deploy không chứng minh GPU animation.
- [ ] Ưu tiên trung hạn: bổ sung ảnh thật từng dòng figure có quyền sử dụng/nguồn; nâng Compare chỉ với tiêu chí được nhà sản xuất hoặc nguồn đáng tin xác minh.
- [x] Nghiên cứu Blender: **khả thi** để dựng một con rồng đúng theo hình minh họa rồi rig xương, weight paint, tạo animation và xuất GLB/glTF. Đây là lộ trình tương lai, **chưa dựng mô hình Blender thực hoặc cài Blender**; không tự chuyển PNG thành model 3D đầy đủ.
- [ ] Chỉ chuyển từ WebGL texture hiện tại sang mô hình Blender khi có mesh/rig đã dựng, kiểm tra dung lượng, chất lượng và WebGL/WebKit; giữ static fallback và không thêm thư viện trước thời điểm cần thiết.

## Chuyển hướng sang mô hình 3D khối / Blender — 17/11/2026
- [x] Người dùng xác nhận PR #5 **chỉ là WebGL 2.5D**; cần rồng thật có thể xoay nhiều góc. Không tiếp tục vá mô hình 2.5D như đã hoàn thành.
- [x] Tách nhánh `feature/kioku-rigged-glb-preview-20261117` dựa trên PR #5, giữ mã PR #5 làm bản tham chiếu hình dáng, palette và nhịp chuyển động; không ảnh hưởng main/Production.
- [x] Tạo mô hình prototype **full-volume 3D** (không phải tấm phẳng): thân tube kín, đầu/mõm, sừng, râu, sống lưng, đuôi, chi/chân; một mesh có vertex color, 11 xương, trọng số đỉnh, hoạt ảnh idle 8 giây và định dạng GLB tại `assets/models/kioku-dragon-rig-v1.glb`. Kiểm tra glTF bằng trimesh: đọc được 9.740 đỉnh, 17.380 tam giác, animation/skin hợp lệ theo kiểm tra cấu trúc; chưa xác nhận chất lượng mỹ thuật.
- [x] Tạo nguồn Python để tái tạo GLB, file hỗ trợ Blender `tools/blender_refine_kioku.py`, README mô hình và trình dựng WebGL đọc GLB có orbit bằng kéo chuột/phím, pause/play, reduced motion, fallback; **không** dùng 2 rồng hoặc CSS giả lập.
- [x] Kiểm thử Chromium nội bộ không có WebGL: phát hiện và sửa lỗi `Cannot access 'paused' before initialization` ở nhánh không hỗ trợ GPU; kiểm thử lại 1440px và 390px không còn pageerror. Đây là kiểm thử fallback, không phải xác minh GPU.
- [ ] **Chưa có Blender trong môi trường**, không cài được do hạn chế kết nối; chưa có file `.blend` được tạo bằng Blender. Mã `blender_refine_kioku.py` là tập lệnh dành cho môi trường Blender, chưa thực thi ở đây. Bản GLB là 3D procedural do ChatGPT dựng, **không phải bản sculpt cao cấp giống 100% mẫu logo**.
- [ ] Đánh giá trực quan mô hình tại nhiều góc, chỉnh tỷ lệ đầu/mặt, sừng, râu, bụng, vảy và bone weight trong Blender rồi mới thay Production. Không báo GPU/Blender PASS khi chưa nghiệm thu.
- [ ] Nhánh PR #6 Preview riêng; giữ nguyên PR #5 và main/Production; chỉ phát hành sau khi có kiểm tra Safari/WebKit, Chromium trên thiết bị thực và người dùng duyệt hình dáng.

## Direct source refinement — 17/11/2026
- [x] Updated `tools/generate_dragon.py` directly in GitHub: staggered volumetric side scale relief, discrete ventral plates, and a smoother head-to-tail travelling bone wave. Existing approved blue silhouette, 11-bone rig, full-width Home and KIOKU Shelf Echo brand remain unchanged.
- [ ] Rebuild `assets/models/kioku-dragon-rig-v1.glb` from updated generator (existing GLB still contains the earlier geometry): `python3 tools/generate_dragon.py` from `kioku-v4/`.
- [ ] Run `node scripts/validate-rig.mjs`, `npm run check`, and `npm run build` on the regenerated GLB. Review multiple orbit angles for scale/scute intersections, eye/face and skin deformation; make changes if needed.
- [ ] Real GPU Safari/Chrome and Cloudflare Preview acceptance still required. The updated source is **not** a verified final 3D sculpt and must not ship to main until regeneration and approval.
- [ ] Codex is release-only per owner request; do not ask it to design, retouch or generate screenshots. Build artifact regeneration required for release is separate from inventing a new dragon.

## River Guardian — tiếp tục từ file Blender của chủ dự án (17/11/2026)
- [x] Chủ dự án cung cấp `KIOKU-River-Guardian-Blender.blend` (Blender 5.3.0 ARM64, macOS 26.0.1) và `KIOKU-River-Guardian-Blender-compatible.glb`, kèm ghi chú thử cục bộ. Ghi chú xác nhận Blender import và phát hoạt ảnh đúng, **đó là kiểm tra trên Mac của người dùng, không phải ChatGPT tự chạy Blender**.
- [x] File GLB tương thích có đúng **10 xương, 6 nhóm vật liệu, 6 giây, 9 rãnh hoạt ảnh xương**; 7.396 đỉnh và 13.176 tam giác khi cộng 6 primitive. Pháp tuyến được chuẩn hóa; trọng số xương tổng bằng 1, chỉ hai tác động khác 0/đỉnh; các khóa đầu/cuối 6 giây trùng nhau.
- [x] Xử lý sai khác từ PR #6: renderer cũ chờ 11 xương, 1 primitive và 8 giây nên không dùng trực tiếp GLB của chủ dự án. Đã sửa `features/shared/dragon-glb-scene.js` để đọc **6 primitive / 6 material**, 10 xương, 6 giây; smooth quaternion slerp; hỗ trợ xoay, Pause/Play, giảm chuyển động, fallback; không tạo rồng thứ hai.
- [x] Xuất `assets/models/kioku-river-guardian-v2.glb` dựa trực tiếp trên binary của GLB chủ dự án, **không thay đổi geometry/bone/animation payload**, chỉ tinh chỉnh roughness/metallic PBR theo 6 vật liệu, điểm nhấn mắt và metadata. Trình kiểm tra GLB riêng xác minh mô hình khớp schema thực tế.
- [x] Tạo `tools/refine_river_guardian_blender.py` cho Blender 5.3 trên Mac: mở **tệp .blend gốc**, smooth shade các phần hữu cơ, chỉnh roughness/metallic, giữ bone/animation 6 giây và xuất **file .blend + .glb mới**, tuyệt đối không ghi đè nguồn. Script này **chưa chạy trong môi trường ChatGPT** vì không cài Blender.
- [x] Node mock WebGL thử đủ 6 draw calls, 10 bone matrices, Pause/Play, reduced-motion và fallback thiếu GPU: PASS. Kiểm tra GLB bằng Python và Node: PASS.
- [ ] Chưa xác minh GPU thực tế trên Safari hoặc Chromium, cũng chưa chạy script Blender hoặc chỉnh model thủ công trong giao diện Blender; **không tuyên bố đã sculpt, weight-paint hay xuất bằng Blender từ container**.
- [ ] Nhánh River Guardian V2 để Preview/Draft; giữ main/Production và PR #5/#6 không merge khi chưa có hình ảnh GPU thực và người dùng phê duyệt.

## River Guardian V4 review — 18/11/2026
- User feedback: V3 still falls short of the original KIOKU blue-dragon illustration; continue improving the existing rigged model.
- Implemented V4 Preview GLB based on uploaded V3: one skinned mesh, 10 bones, 6 materials, 9 rotation tracks, 6-second seamless swim.
- Visual changes: removed duplicate V3 horns/whiskers, added layered navy/teal mane, narrow brow/eyes, sparse skinned flank details, slim nose, tail streamers and claws; no separate dragon.
- Motion QA (CPU, at 1.5s relative to t0): mid-body V3 0.0523 units -> V4 0.1198; tail V3 0.9342 -> V4 1.712. It is animated bone deformation, not camera orbit alone.
- Reverted floating belly seam experiment after inspecting QA views; model still requires hand-sculpt refinement of head, legs and scales.
- Verified GLB container, 10 joints, 9 channels, 6 materials, 12,362 vertices and 20,064 triangles; CPU-projected five-view QA and 6s GIF generated, not GPU/browser render.
- V4 generator and review report are committed; renderer/build/validator/check target the new GLB on a dedicated Preview branch.
- Remaining: manual Blender 5.3 sculpt/weight-paint, visual likeness approval, Safari/Chromium GPU QA and accessibility controls. Never merge to Production without owner approval.
