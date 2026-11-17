# KIOKU — Design Rules (Canonical)

**Dự án:** KIOKU V6 · Shelf Echo. Đây là quy tắc thiết kế riêng của Kioku, **không** phải `design-rules.md` của Momo Matcha.

## 1. Ý niệm và sự thật văn hóa
- KIOKU (記憶 / きおく) nghĩa là ký ức / sự hồi tưởng; "time flows, memories remain" là **ẩn dụ thương hiệu**, không phải cách dịch từ nguyên.
- Trục nhận diện: ký ức anime, vật thể sưu tầm, thời gian và văn hóa thị giác Nhật Bản **đương đại**. Kết hợp mỹ thuật biên tập và UX sưu tầm rõ ràng; không biến web thành poster thiếu chức năng.
- Nhận diện **Shelf Echo** (logo, wordmark, favicon, các file SVG trong `brand/`) là mốc V6 hiện tại. Không thay logo hoặc token chỉ vì thẩm mỹ mặc định của model. Mọi redesign tiếp theo cần brief rõ và review Preview.
- Không "Á Đông hóa" bằng hoa anh đào, cổng torii, dấu son, mặt trời mọc, Hán tự/kanji, mây, sen hay nghi thức không có căn cứ. Chữ tiếng Nhật chỉ dùng khi đúng nghĩa và có ngữ cảnh. Không mượn nhãn hiệu Bandai/MegaHouse làm logo Kioku.

## 2. Hình ảnh và nội dung
- **Ảnh của đúng món hàng** là nguồn sự thật khi bán pre-owned/no-box. Không thay bằng AI render hoặc ảnh generic khiến khách tưởng là món thực tế.
- Trang sản phẩm phải tách identity của model (manufacturer, line, series, character, edition) khỏi **physical item** (ảnh riêng, phụ kiện, lỗi, tình trạng, hộp, số lượng).
- Chưa có ảnh/tình trạng/giá/tồn/nguồn gốc xác minh: chỉ hiển thị **catalogue reference**, không có "Add to cart" hoặc lời khẳng định hàng đang bán.
- Không bịa số collector, sản phẩm limited, rating, review, giải thưởng, chứng nhận authentic, sealed, xuất xứ Nhật, vận chuyển quốc tế hay ETA.
- Nội dung công khai English 100%, lời văn tự nhiên, ngắn gọn, chính xác; không dùng copy filler.

## 3. Huashu art direction + anti-AI-slop
- Hình thức phải xuất phát từ sản phẩm và câu chuyện, không bắt đầu bằng template màu/serif.
- Không mặc định nền kem + serif + màu son; cũng không mặc định nền tối neon, glassmorphism, gradient ảo, bento, bo tròn đồng loạt hay shadow dày. Chỉ dùng khi có lý do từ nội dung.
- Tránh hero lớn → 3 card giống nhau → quote → CTA; tránh eyebrow ALL CAPS ở mọi section, đánh số 01/02/03 vô nghĩa, icon/emoji và mũi tên trang trí dày đặc.
- Mỗi màn có một **sự kiện thị giác riêng**: ảnh hiện vật, danh mục có cấu trúc, câu chuyện hoặc thao tác hữu ích. Các section kế tiếp phải khác nhịp vì thông tin, không vì ngẫu hứng.
- Hình ảnh quan trọng hơn đồ trang trí; khoảng trắng có quan hệ với chủ thể, không dựng trang trống giả "Zen".
- Khi thực hiện redesign lớn: nghiên cứu tham chiếu thực → six thumbnails → 3 hướng bố cục khác nhau → chọn hướng → desktop/mobile polish ≥2 vòng. Không gọi ba bản đổi màu là ba hướng. Ghi quyết định đã được duyệt, tránh mở lại vô hạn.
- Ưu tiên Huashu `SKILL.md`, `references/directions.md`, `modules/web.md`, `content-guidelines.md`, `typography.md`, `materials.md`, `polish-loop.md`. EvondevKit hỗ trợ UX và component behavior.

## 4. Điều hướng và hệ trang V6
- 7 trang: Home, Collection, Figure Finder, line Reference Detail, Condition Guide, Journal, About.
- Giữ các tương tác đã có: Global Search, shareable maker/line filter và sort, Saved References, Compare tối đa 3, Finder 3 câu hỏi, reference zoom, condition note copy/export, mobile navigation.
- Trang chủ giới thiệu chính xác nội dung và hai maker chính; không khiến catalogue reference trông như hàng sẵn bán.
- Collection: lọc theo dữ liệu có thật; trường hợp không kết quả có reset; URL chia sẻ được. Search không được giả kết quả. UI đủ dùng bằng bàn phím.
- Reference Detail: ảnh đúng loại dữ liệu, zoom/close/Escape, tình trạng hàng thực chỉ xuất hiện khi có actual item được kiểm chứng.
- Condition Guide: `figure_condition`, `box_condition`, `accessories`, `missing_parts`, `observed_defects` là các trường độc lập; không copy hạng điểm của Mandarake/AmiAmi hoặc nói Kioku đã kiểm định nếu chưa có dịch vụ đó.
- Finder và Compare là công cụ **tham khảo dòng figure**, không gợi ý tồn kho thật.

## 5. Typography, vật liệu, responsive và accessibility
- Typography tối đa 2 họ chính; body 16–18px, mobile ≥16px; 4–5 cấp phân cấp, line length dễ đọc; logo không tự thay bằng font tương tự.
- Không bịa màu HEX "truyền thống". Dùng palette/token đã thống nhất với Shelf Echo; thêm màu chỉ khi có chức năng và kiểm tra tương phản ≥4.5:1 cho chữ thường, ≥3:1 cho chữ lớn.
- Thiết kế mobile là một bố cục độc lập, không thu nhỏ máy móc grid desktop. Thử 320/375/390/768/1440px; tap target ≥44×44px, focus rõ, menu có aria state, overlay đóng bằng Escape.
- `prefers-reduced-motion`; animation phục vụ thao tác, không auto-play âm thanh, không horizontal-scroll cưỡng bức, không gây CLS. Giữ tỷ lệ ảnh hiện vật; dùng `object-fit:contain` khi cần thấy toàn bộ.
- Test build, link, browser console, keyboard, empty/selected/error states. Không báo Lighthouse/Safari/Cloudflare QA PASS nếu chưa có bằng chứng.

## 6. Vận hành thương mại (chưa tự bật)
- Muốn bán thật phải có dữ liệu từng SKU/món: ảnh của đúng món + quyền sử dụng, manufacturer/line, tình trạng figure và box tách biệt, phụ kiện/lỗi, giá-tiền tệ, tồn kho, nguồn gửi, chính sách đổi trả/vận chuyển.
- Checkout cần backend kiểm tra giá/tồn, reservation chống hai khách mua món độc bản, idempotency chống đơn kép và đối soát thanh toán thực. Không đánh dấu "paid" chỉ vì người dùng bấm nút.
- Kioku là seller độc lập; không tự nhận official seller/authorized distributor của Bandai hoặc MegaHouse.

## 7. Hàng rào dự án
Tệp này chỉ nằm ở `kioku-v4/design-rule.md`. **Không copy/sync/ghi đè** sang `momo-matcha-can-tho/design-rules.md`. Repo khác nhau, brand asset khác nhau, môi trường deploy khác nhau. Dùng chung phương pháp thiết kế không đồng nghĩa dùng chung brand.

## 8. Art direction hiện hành — yêu cầu 17/11/2026 (Preview đang duyệt)
- Tham khảo tinh thần bố cục của mẫu người dùng gửi: nền **midnight/indigo gần đen**, sắc tím lavender làm nhấn, nhịp thị giác rõ, ảnh/đối tượng chính nổi bật; không sao chép logo, đồ họa, nội dung hay cấu trúc độc quyền của mẫu.
- Header/navigation desktop dùng toàn chiều ngang trình duyệt. Home có **một sân khấu rồng 3D lớn toàn bề ngang**; phần câu chuyện, tiêu đề và liên kết Collection/Finder được đặt **dưới** sân khấu, tiếng Anh 100%.
- Mẫu rồng trên Home là tác phẩm nguyên bản có chiều sâu 3D thực (WebGL hoặc mô hình 3D được cấp phép), chuyển động tinh tế và tương tác con trỏ khi phù hợp; phải có fallback hình tĩnh, tắt chuyển động khi người dùng bật `prefers-reduced-motion`.
- Giữ logo, thông tin danh mục và toàn bộ công cụ collector đã có; không tạo dữ liệu hàng hóa, doanh số hay liên kết mua hàng không xác thực.
- Dải màu đã được người dùng chấp nhận về hướng thiết kế (nền `#0B0D17`, chữ `#F4F2FA`, nhấn `#C5A7FB`), nhưng chỉ phát hành Production sau khi kiểm chứng bản sửa cuối cùng.

## 9. Quyết định đã duyệt về linh vật và logo — 17/11/2026
- **Giữ nguyên hình dáng đã duyệt của rồng KIOKU**: không thay model, silhouette, màu vật liệu, sừng/mặt/đuôi, bố cục hoặc nhịp chuyển động tổng thể chỉ vì stylistic preference.
- Tinh chỉnh có chủ đích: **thân rồng uốn lượn thêm một chút**, là chuyển động sóng truyền dọc sống lưng và trễ pha; vùng đầu gần như ổn định, biên độ tăng dần về đuôi; giữ hoạt ảnh nhã, không quẫy giật hoặc đuôi lắc quá mạnh.
- Biến dạng áp dụng trong WebGL vertex shader của `features/shared/dragon-scene.js` trên mesh gốc, không phải ảnh 2D giả 3D. Cập nhật pháp tuyến tương ứng để vật liệu không bị sai ánh sáng. Giữ fallback tĩnh và reduced-motion.
- Dùng **đúng file brand đã có** `brand/kioku-lockup-light.svg` ở header và dấu thương hiệu trong hero; không vẽ lại logo hoặc lấy logo đối thủ. Giữ hero full-width và phần giới thiệu bên dưới.
- Thay đổi phải được kiểm chứng ở cả mobile/desktop; chỉ sửa mã nguồn KIOKU, không động tới logic collector hoặc hàng hóa.

## 10. Logo rồng xanh do chủ thương hiệu cung cấp
- Người dùng đã đưa artwork tham chiếu có rồng xanh thân dài, đầu có sừng/râu, bụng sáng phân đốt, uốn qua chữ KIOKU. **Đó là hình ảnh nhận diện cần hiển thị trên Home**, không chỉ bản mesh procedural WebGL.
- Home giữ mô hình 3D đã duyệt làm hiệu ứng nền, nhưng logo/rồng nguyên bản từ tờ mẫu nằm trên lớp foreground. Có thể dùng bản SVG truy nét từ ảnh gốc ở `assets/img/kioku-owner-dragon-logo.svg`; bản truy nét có giảm chi tiết màu so với source, không được nhận là file vector gốc của tác giả.
- Đảm bảo màu chữ logo navy đọc rõ trên nền giấy sáng. Không thay artwork thương hiệu bằng ảnh AI tạo mới hoặc các con rồng khác. Nếu có file vector gốc chất lượng cao, ưu tiên thay thế đúng asset này sau khi được chủ thương hiệu phê duyệt.

## 11. Đính chính ưu tiên cao — hình rồng phải là kết cấu của mô hình chuyển động
- Mô hình **một rồng duy nhất**: rồng xanh trong mẫu của chủ thương hiệu phải tham gia chuyển động 3D; **không** tách SVG/logo tĩnh thành một rồng và dựng thêm rồng 3D khác đằng sau.
- Hình vẽ nguồn là texture của một lưới WebGL chuyển động theo sóng thân–đuôi (đầu gần ổn định). Chữ KIOKU có thể đứng yên trong cùng sân khấu, miễn là không tạo hai con rồng.
- Giữ nhận diện hình dáng đầu, sừng/râu, lớp bụng sáng, phối màu xanh; không tự tạo lại rồng bằng ảnh sinh AI. Không phóng đại WebGL textured surface thành rigged mesh 3D hoàn chỉnh.
- Hoạt ảnh phải có `prefers-reduced-motion` và fallback tĩnh khi GPU/WebGL lỗi. Không thể coi Cloudflare build success là bằng chứng hoạt ảnh render thành công.
