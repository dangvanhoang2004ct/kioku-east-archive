# KIOKU — Quy tắc thực thi dự án

> Chỉ áp dụng cho repository `dangvanhoang2004ct/kioku-east-archive`, thư mục mã website `kioku-v4/`. Không áp dụng cho Momo Matcha hoặc RoleFit.

## Đầu phiên
1. Đọc `dang-lam.md` và `ghi-chu/muc-luc.md` trước; sau đó chỉ đọc ghi chú liên quan.
2. Đọc `design-rule.md` khi sửa branding/UI/copy; giữ đúng hệ nhận diện **Shelf Echo** của KIOKU V6 hiện hành. Không lấy quy tắc từ file `design-rules.md` của Momo.
3. Đối chiếu `main`, PR và build source trước khi sửa. Ghi chú là checkpoint, không thay thế bằng chứng runtime.
4. Ưu tiên patch nhỏ đúng chức năng. Không xây lại website, không thêm framework, dashboard, dịch vụ hoặc tài liệu trùng lặp.

## Nguồn sự thật và phạm vi
- Repo: `dangvanhoang2004ct/kioku-east-archive`; mã web nằm trong `kioku-v4/`.
- Nền tảng: Cloudflare Pages riêng của Kioku; Production `https://kioku-east-archive.pages.dev/`. Chỉ deploy Preview cho thay đổi mới, merge/publish Production khi chủ thương hiệu đồng ý và có bằng chứng nghiệm thu.
- KIOKU là thương hiệu độc lập về anime figures; Bandai Spirits và MegaHouse là nhóm nhà sản xuất được ưu tiên phân loại, **không** đồng nghĩa quan hệ đối tác/ủy quyền.
- Website khách hàng **English 100%**, mobile-first. Tách danh mục dòng figure để tham khảo khỏi từng món vật lý đang bán.
- Không tự tạo SKU, ảnh hàng thật, giá, tồn kho, chứng nhận, đánh giá, chính sách, checkout, giao dịch hoặc kết quả kiểm định. Ảnh minh họa phải được ghi rõ là reference/concept.

## Phương pháp
- **Huashu** dẫn dắt concept, brand, bố cục, vật liệu, typography, anti-AI-slop và vòng đánh giá.
- **EvondevKit** dẫn dắt điều hướng, tương tác, responsive, khả năng truy cập, trạng thái loading/empty/error.
- Kiểm tra từng hành động có tác dụng thật; giữ Search, Filter/Sort, Favorites, Compare, Finder, Zoom, Condition Notes copy/export.
- Tái sử dụng kiểm thử PASS còn phù hợp, kiểm thêm phần đã thay đổi; không yêu cầu Codex chụp ảnh; phân biệt kết quả QA báo cáo và QA tự xác minh.

## Ranh giới bắt buộc
- Không đọc/sửa/copy tài sản, endpoint, secret, mã nguồn hoặc design rules của Momo khi thực hiện nhiệm vụ Kioku.
- Không ghi đè `kioku-v4/design-rule.md` bằng tài liệu Momo; không tạo bản `design-rules.md` thứ hai cho Kioku.
- Không sửa dữ liệu giao dịch, ảnh/claim về hàng thật hoặc thay nhận diện đã duyệt nếu yêu cầu không liên quan.
- Không lộ API key hoặc dữ liệu khách hàng ở frontend, PR, logs hay ghi chú.

## Báo cáo
Rất ngắn: **Đã làm / Kiểm thử / Chưa làm được / Cần hỗ trợ**. Ghi rõ branch/commit/PR/Preview, không nhận PASS khi chưa kiểm chứng.
