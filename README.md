# NhacMix 1.5 — Android + Web/PWA

Ứng dụng nghe nhạc tiếng Việt, quản lý thư viện nhạc/video trên thiết bị, playlist và lưu link bài hát từ website. Android có foreground media service và MediaSession để điều khiển phát nhạc nội bộ từ thông báo/màn hình khóa.

## Tính năng
- Thêm video YouTube bằng trình phát nhúng chính thức. Quảng cáo và giới hạn phát nền do YouTube kiểm soát.
- Chọn nhiều file nhạc/video từ thiết bị: MP3, M4A, WAV, OGG, FLAC, AAC, OPUS, WMA, MP4, WebM và các định dạng thiết bị hỗ trợ.
- Chuyển video MP4 trực tiếp được phép sử dụng thành MP3 bằng FFmpeg.wasm trên thiết bị/trình duyệt (URL trực tiếp, máy chủ cho phép CORS, giới hạn 200 MB).
- Lưu link trang bài hát từ website (ví dụ Zing MP3) vào thư viện, thêm link vào playlist và mở website chính thức qua trình duyệt ngoài. Đây là mục lưu liên kết, không phải trình phát âm thanh trực tiếp; phát nền phụ thuộc website nhà cung cấp.
- Playlist, thêm/bỏ bài, xóa bài khỏi thư viện, yêu thích, lịch sử nghe, tìm kiếm, giao diện sáng/tối.
- Android: dịch vụ foreground `NhacMixMediaService`, `MediaSessionCompat` và thông báo có nút trước/phát-tạm dừng/tiếp/dừng cho nhạc/video nội bộ. Hành động từ thông báo gửi về trình phát trong app.
- PWA và icon app; GitHub Actions build APK debug và AAB ký bằng keystore riêng.

## Các tính năng đã bỏ
- Đã bỏ mục phát URL MP3 public trực tiếp vì không ổn định với nhiều máy chủ. Các mục `publicAudio` cũ bị lọc khỏi thư viện khi ứng dụng khởi động.
- Không phát nhạc trực tiếp bên trong NhacMix từ URL trang website. Website link được lưu vào thư viện/playlist và mở bằng trình duyệt chính thức.

## Quyền truy cập tệp
NhacMix dùng bộ chọn tệp của hệ điều hành (`input type=file`) theo Scoped Storage. Người dùng chọn những file cụ thể; app không yêu cầu quyền đọc toàn bộ bộ nhớ. File được lưu trong IndexedDB của ứng dụng. Giữ bản gốc vì dữ liệu web có thể bị xóa khi gỡ app, xóa dữ liệu hoặc thiếu dung lượng.

## Điều khiển media Android
Khi phát file nhạc/video nội bộ trong APK, app khởi chạy foreground service và MediaSession để Android hiển thị thông báo điều khiển. Có thể tạm dừng/phát, chuyển bài và dừng từ thông báo. Android 13+ có thể yêu cầu quyền thông báo. YouTube và link website không được quản lý bởi service này; nền và điều khiển của chúng phụ thuộc nền tảng tương ứng.

## Chạy Web/PWA
Yêu cầu Node.js 20+:
```bash
npm install
npm start
```
PWA cần HTTPS hoặc localhost. Dữ liệu lưu riêng theo origin, không tự đồng bộ giữa web và Android. Web/PWA dùng Media Session API của trình duyệt; không có foreground service native.

## Build APK debug
1. Push source lên GitHub branch `main`.
2. Actions → **Build NhacMix Android APK** → Run workflow.
3. Workflow tạo Android project, chạy `scripts/patch-android-media.py`, sync plugin và build APK.
4. Tải artifact `NhacMix-debug-apk`.

## Build AAB ký số để phát hành Google Play
### 1. Tạo keystore
Dùng Android Studio **Build → Generate Signed Bundle / APK → Android App Bundle** hoặc `keytool`. Sao lưu keystore an toàn, không commit keystore/mật khẩu vào GitHub.

### 2. Thêm GitHub Actions Secrets
Repository → Settings → Secrets and variables → Actions:
- `ANDROID_KEYSTORE_BASE64`: nội dung base64 của file `.jks`.
- `ANDROID_KEYSTORE_PASSWORD`: mật khẩu keystore.
- `ANDROID_KEY_ALIAS`: alias của key.
- `ANDROID_KEY_PASSWORD`: mật khẩu key.

Linux/macOS: `base64 -w 0 release-key.jks` (macOS có thể dùng `base64 release-key.jks | tr -d '\n'`). Windows PowerShell: `[Convert]::ToBase64String([IO.File]::ReadAllBytes('release-key.jks'))`.

### 3. Chạy workflow
Actions → **Build NhacMix signed Android AAB** → Run workflow. Khi thành công, tải artifact `NhacMix-release-signed-aab` chứa `app-release.aab`. Build sẽ dừng nếu secrets chưa hợp lệ.

## Kiểm thử cần làm trước khi phát hành
- Build cả APK và AAB trên GitHub Actions.
- Trên Android thật: cấp quyền thông báo, phát file MP3, khóa màn hình, thử nút phát/tạm dừng/trước/tiếp/dừng từ notification và tai nghe Bluetooth.
- Thử file lớn, đổi bài liên tục, cuộc gọi đến và thao tác xóa bài/playlist.
- Link website chỉ mở trang chính thức; không đảm bảo website cho phép phát nền.

## Cấu trúc
- `www/`: giao diện web/PWA.
- `assets/`: icon và splash.
- `scripts/patch-android-media.py`: bổ sung plugin/service Android khi CI tạo project mới.
- `.github/workflows/build-apk.yml`: APK debug.
- `.github/workflows/build-android-aab.yml`: AAB release ký bằng GitHub Secrets.

**Trạng thái:** đã kiểm tra cú pháp JavaScript và Python, nhưng chưa chạy build Gradle hoặc kiểm thử trên thiết bị Android thật trong môi trường này.


## Phiên bản 1.5.3
- Chỉ tạo MediaSession Android cho file âm thanh trong thiết bị (`type=local`, không phải video).
- Link/video YouTube không tạo player media nền của NhacMix; khi chuyển sang YouTube sẽ dừng phiên media native của file nhạc trước đó.
- APK CI được xuất tên `NhacMix-v1.5.3-versionCode16-debug.apk`; AAB release nếu cấu hình đủ khóa ký sẽ có tên `NhacMix-v1.5.3-versionCode16-release.aab`.
