# NhacMix 1.1 — Android + Web/PWA

Ứng dụng tiếng Việt kết hợp link YouTube qua trình phát chính thức và thư viện âm thanh/video do người dùng chọn trên thiết bị.

## Tính năng
- Thêm link YouTube video, youtu.be, Shorts và embed; phát qua YouTube IFrame Player API chính thức.
- Nhập file audio (MP3, M4A, WAV, OGG, FLAC, AAC, OPUS, WMA) và video (MP4, M4V, WebM, MOV, MKV, 3GP, AVI) qua bộ chọn tệp của hệ điều hành/trình duyệt.
- File đã chọn được lưu vào IndexedDB trong app/web origin. Kiểm tra bộ nhớ ước tính trong giao diện.
- Phát audio/video cục bộ, điều khiển tiến trình, âm lượng, bài trước/tiếp và dừng hẳn.
- Playlist, yêu thích, lịch sử nghe, tìm kiếm, giao diện sáng/tối.
- Icon app SVG/PNG và workflow APK debug + AAB release ký bằng keystore do người dùng quản lý.

## Quyền truy cập tệp và thư mục
NhacMix dùng bộ chọn tệp hệ thống (`input type=file`) nên Android mở bộ chọn Documents/Media và người dùng chọn những file cụ thể. Đây là cách ưu tiên theo Scoped Storage; app không yêu cầu quyền truy cập toàn bộ bộ nhớ hoặc quyền quản lý mọi file. Không có quyền truy cập liên tục vào một thư mục tùy ý; người dùng cần chọn file lại nếu dữ liệu đã bị xóa khỏi kho app. File đã nhập được lưu trong IndexedDB, có thể bị hệ điều hành/trình duyệt dọn khi thiếu dung lượng hoặc khi dữ liệu app bị xóa. Giữ bản gốc của tệp.

## Phát nền và giới hạn
- Audio/video cục bộ phát bằng HTML media. Việc tiếp tục phát khi khóa màn hình phụ thuộc WebView, trình duyệt, chế độ tiết kiệm pin và hệ điều hành; source này chưa tích hợp dịch vụ Android foreground-media chuyên dụng nên chưa cam kết phát nền ổn định khi màn hình khóa.
- YouTube chạy trong trình phát chính thức. Không chặn quảng cáo, trích xuất audio hoặc vượt hạn chế phát nền. Trải nghiệm nền/quảng cáo phụ thuộc YouTube và dịch vụ/tài khoản chính thức.
- Một số codec video (đặc biệt MKV/AVI hoặc codec lạ) có thể không phát được trên thiết bị; MP4 H.264/AAC là lựa chọn tương thích rộng hơn.

## Chạy Web/PWA
Yêu cầu Node.js 20+:
```bash
npm install
npm start
```
PWA cần HTTPS hoặc localhost. Dữ liệu lưu riêng theo origin, không tự đồng bộ giữa web và Android.

## Build APK debug
1. Push source lên GitHub branch `main`.
2. Actions → **Build NhacMix Android APK** → Run workflow.
3. Tải artifact `NhacMix-debug-apk`.

## Build AAB ký số để phát hành Google Play
### 1. Tạo keystore riêng, giữ an toàn
Dùng Android Studio **Build → Generate Signed Bundle / APK → Android App Bundle** để tạo keystore, hoặc `keytool` từ JDK. Sao lưu keystore an toàn. Không commit keystore/password vào GitHub.

### 2. Thêm GitHub Actions Secrets
Repository → Settings → Secrets and variables → Actions → New repository secret:
- `ANDROID_KEYSTORE_BASE64`: nội dung base64 của file keystore `.jks`.
- `ANDROID_KEYSTORE_PASSWORD`: mật khẩu keystore.
- `ANDROID_KEY_ALIAS`: alias của key.
- `ANDROID_KEY_PASSWORD`: mật khẩu key.

Linux/macOS tạo base64 bằng `base64 -w 0 release-key.jks` (trên macOS dùng `base64 release-key.jks | tr -d '\n'`). Trên Windows PowerShell có thể dùng `[Convert]::ToBase64String([IO.File]::ReadAllBytes('release-key.jks'))`.

### 3. Chạy workflow
Actions → **Build NhacMix signed Android AAB** → Run workflow. Khi build thành công, tải artifact `NhacMix-release-signed-aab` chứa `app-release.aab`.

Workflow sẽ dừng nếu chưa có secrets hợp lệ. Đây là cấu hình build dự kiến; cần chạy CI thật, kiểm tra AAB bằng Play Console/internal testing và hoàn tất thông tin ứng dụng/chính sách trước phát hành. Không dùng lại keystore bị mất; bản cập nhật phải ký đúng key hoặc dùng Play App Signing theo cấu hình tài khoản.

## Icon
- `assets/icon.svg`: nguồn vector.
- `assets/icon.png`: icon 1024x1024 dùng để tạo Android launcher icons.
- `assets/splash.png`: nền splash.
- `www/icon.svg`, `www/icon-512.png`: icon PWA.

## Cấu trúc
- `www/`: web app/PWA.
- `assets/`: icon và splash cho Android.
- `.github/workflows/build-apk.yml`: APK debug.
- `.github/workflows/build-android-aab.yml`: AAB release ký bằng GitHub Secrets.
