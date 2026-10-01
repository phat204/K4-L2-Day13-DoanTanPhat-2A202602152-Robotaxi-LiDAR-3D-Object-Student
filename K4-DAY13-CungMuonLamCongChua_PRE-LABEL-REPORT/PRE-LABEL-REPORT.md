# Báo cáo thực hành PointPillars — Day 13

## 1. Thông tin nhóm

- Mã nhóm: K4-DAY13-Cũng Muốn Được Làm Công Chúa Cơ
- Danh sách thành viên, MSSV và phân công: xem [TEAMMATES.md](TEAMMATES.md).
- Mục tiêu: chạy thử PointPillars trên PCD demo, phân tích A/B/C và nhận diện lỗi batch vs lỗi từng hộp trước khi bắt đầu chỉnh cuboid trên CVAT.
- Tài liệu tham khảo: PRE-LABEL.md, README-STUDENT.md, PRE-LABEL-REPORT.md.

## 2. Cấu hình chạy thử

- PCD: `demo.pcd`
- Score threshold: 0.3
- ROI: front-window. Các vật nằm ngoài vùng phía trước này không xuất hiện trong output do bị giới hạn phạm vi inference; không xem đó là model bỏ sót.
- Kiểm tra A/B/C trên cùng một PCD, giữ checkpoint và mục tiêu inference không đổi.
- Chất liệu đầu vào: PCD demo đã được chuyển đổi cho mục đích thực hành, không dùng Robotaxi và không import kết quả vào CVAT.
- Smoke status: `passed`; các bước load image, A, B, C và QC đều `passed` (`ket-qua-nhom-01/smoke.json`).
- Người vận hành theo phân công lượt: xem [TEAMMATES.md](TEAMMATES.md); `smoke.json` không ghi tên người chạy theo từng bước.
- Runtime: Linux amd64, 4 CPUs, memory limit `4g`; image ID `sha256:e03983bd922ec29890bf547db8de408402efd82583680b62e671c20da2fd2c82`.
- Checkpoint: `/opt/PointPillars/pretrained/epoch_160.pth`, SHA-256 `482dfcf63b932cc5ccf012b4bbdad52aa51aa33becf87d0a39d61c39b377b5b1`.
- Input SHA-256: `3b5ea3da13e2b19149cab6a8d521c2ca55f2df93f026b5a3f8c273ce70645d60`; `z_ground = 0.075 m` (theo JSON/manifest kết quả).
- Code provenance: revision `0831856d921609312d42c7582c366e5a311bb7b1`, working tree dirty; `preannotate.py` SHA-256 `65edf6ac95926f799c27f2c30c8595b0da4e8e2429f0c1a9aedf5c9e1fceb5ca`, helper SHA-256 `c177fc008f79223e94b8c06423d3a806e422787d48c8d39f1c5fd3ce2c4eeaa7`.

| Bước | Trạng thái | Thời gian UTC ngày 01/10/2026 | Thời lượng | Số hộp | Prediction SHA-256 |
| --- | --- | --- | ---: | ---: | --- |
| `docker-load` | `passed` | 08:04:11.559–08:05:14.378 | 62.812 s | - | - |
| `run-A` | `passed` | 08:05:14.610–08:05:30.557 | 15.954 s | 1 | `465245f95d7c914d5fafc724dec0853a0fe45492ab34a491b03366f774376f5e` |
| `run-B` | `passed` | 08:05:30.559–08:05:42.543 | 11.984 s | 13 | `2ffb4e85d1a8746b1f290f6704204bf57e5521ae3df98ea81473a087a066fcfc` |
| `run-C` | `passed` | 08:05:42.545–08:05:52.045 | 9.500 s | 6 | `a595d0dc3d570d83d3e1de50ca84e196f9291d05c40598e7442ef6211bc4ceac` |
| `qc-cases` | `passed` | 08:05:52.047–08:05:56.521 | 4.469 s | - | - |

## 3. Kết quả ba lượt A/B/C

| Lượt | delta | Pillar XY | Số hộp | mean_z | File output chính | Nhận xét |
| --- | --- | --- | --- | --- | --- | --- |
| A | 0 | 0.16 | 1 | 0.330 | `run-A/summary.csv`, `run-A/boxes-demo-delta-0-voxel-0.16.json` | Mốc so sánh với delta bằng 0. |
| B | 1.73 | 0.16 | 13 | 1.034 | `run-B/summary.csv`, `run-B/boxes-demo-delta-1.73-voxel-0.16.json` | Thí nghiệm đổi delta trước inference; 10 vehicles, 1 two-wheels, 2 pedestrian. |
| C | 1.73 | 0.32 | 6 | 1.091 | `run-C/summary.csv`, `run-C/boxes-demo-delta-1.73-voxel-0.32.json` | Thí nghiệm đổi pillar XY; 6 pedestrian, 0 vehicles. |

## 4. Phân tích so sánh

### 4.1 So sánh A và B
- Giữa A và B, nhóm đổi delta từ 0 m lên 1.73 m trước khi model chạy. Phép đổi thuận là `z_model = z_source - z_ground - delta`; sau inference, phép đổi ngược là `z_source = z_model + delta + z_ground`.
- Delta làm thay đổi z của input model nhận. Model chạy trên input khác nên có thể tạo số lượng và lớp prediction khác; A có 1 hộp, B có 13 hộp là kết quả thí nghiệm, không phải lỗi pipeline.
- B có 10 vehicles, 1 two-wheels và 2 pedestrian (`run-B/boxes-demo-delta-1.73-voxel-0.16.json`).

### 4.2 So sánh B và C
- Khi giữ nguyên delta nhưng tăng pillar XY từ 0.16 lên 0.32, số hộp giảm từ 13 xuống 6.
- JSON lượt C có 6 hộp `pedestrian` và 0 hộp `vehicles` (`run-C/boxes-demo-delta-1.73-voxel-0.32.json`). Checkpoint PointPillars KITTI được train với pillar XY 0.16 m.
- Pillar 0.32 m gom điểm trên ô lớn hơn, làm lưới XY thô hơn và thay đổi đặc trưng không gian so với cấu hình train; vì vậy lớp/số hộp có thể đổi. Đây là lời giải thích hợp lý cho output lạ, nhưng chưa đủ bằng chứng để khẳng định nguyên nhân duy nhất hay độ chính xác.
- Số hộp nhiều hơn hoặc mean_z khác không tự động chứng minh prediction “đúng hơn”; cần nhìn vào hình học, ROI, và các view phản ánh đúng không gian 3D.

### 4.3 Cách đọc bằng chứng
- A/B/C là các lượt inference thí nghiệm: nhóm chủ ý đổi delta hoặc pillar; khác biệt output không tự nó là lỗi pipeline.
- Chỉ `case-batch-z` mô phỏng lỗi pipeline: bỏ phép đổi z ngược sau inference làm z của toàn bộ hộp sai cùng lượng, còn số hộp và các trường khác giữ nguyên.
- Đối chiếu JSON và ảnh Side để phân biệt batch-level với object-level; Side view chỉ là gợi ý quan sát, không đủ kết luận chính xác từng hộp.

## 5. Ca QC có kiểm soát

| Ca | Số hộp lệch / tổng | Độ lệch z | Trường không đổi / kết luận |
| --- | ---: | ---: | --- |
| `case-correct` | 0/13 | 0 m | Prediction nguồn để đối chiếu, không phải ground truth. |
| `case-batch-z` | 13/13 | −1.805 m mỗi hộp | Chỉ z đổi; label, x, y, length, width, height, yaw và score giữ nguyên. Lỗi bỏ phép đổi z ngược. |
| `case-one-box-z` | 1/13 | −1.805 m ở hộp đầu tiên | Chỉ z của một hộp đổi; các trường khác giữ nguyên. Lỗi cục bộ mô phỏng. |

- Chúng ta không import các file `case-*.json` vào CVAT hay dùng làm ground truth.
- Các ca này chỉ là ví dụ học tập để phân biệt lỗi batch và lỗi từng hộp.

## 6. Phân công công việc trong nhóm

Vai trò theo từng lượt được ghi trong [TEAMMATES.md](TEAMMATES.md).

## 7. Nhận xét cá nhân

### Thành viên 1
- Vai trò: vận hành runner, ghi log và lưu output A/B/C.
- Quan sát: A có 1 hộp và B có 13 hộp; cả hai lượt `passed` (`ket-qua-nhom-01/smoke.json`).
- Phép z: trước model `z_model = z_source - z_ground - delta`; sau model `z_source = z_model + delta + z_ground`.
- Quyết định khi gặp lỗi batch: nếu toàn bộ hộp cùng lệch −1.805 m như `case-batch-z.json`, dừng để kiểm tra phép đổi ngược; A/B khác nhau là thí nghiệm.
- Điều chưa chắc: không có ground truth nên chưa thể kết luận prediction A hay B đúng hơn.

### Thành viên 2
- Vai trò: kiểm cấu hình, đọc `summary.csv` và so sánh B/C.
- Quan sát: B gồm 10 vehicles, 1 two-wheels, 2 pedestrian; C gồm 6 pedestrian (`run-B` và `run-C` JSON).
- Phép z: trước model `z_model = z_source - z_ground - delta`; sau model `z_source = z_model + delta + z_ground`.
- Quyết định khi gặp lỗi batch: dừng nếu mọi hộp cùng sai z và trường khác không đổi như `case-batch-z`; không coi đổi phân bố giữa B/C là lỗi pipeline.
- Điều chưa chắc: chưa thể xác định vì sao C chỉ dự đoán pedestrian hoặc lớp nào đúng nếu chưa đối chiếu ground truth.

### Thành viên 3
- Vai trò: theo dõi JSON và ảnh Side, đối chiếu hình học giữa các lượt.
- Quan sát: so với `case-correct.json`, `case-batch-z.json` đổi z của 13/13 hộp đúng −1.805 m; các trường khác giữ nguyên.
- Phép z: trước inference trừ `z_ground + delta`; sau inference cộng lại `z_ground + delta` để về hệ nguồn.
- Quyết định khi gặp lỗi batch: dừng và kiểm tra phép đổi ngược; nếu chỉ một hộp lệch như `case-one-box-z`, kiểm tra riêng hộp đó.
- Điều chưa chắc: ảnh Side không đủ để xác nhận chính xác kích thước, yaw hay tính đúng của từng hộp.

### Thành viên 4
- Vai trò: so sánh QC cases và tổng hợp cách phân biệt lỗi batch với lỗi một hộp.
- Quan sát: `manifest.json` ghi offset 1.805 m và 13 hộp; `case-correct` lệch 0/13, `case-batch-z` lệch 13/13, `case-one-box-z` lệch 1/13.
- Phép z: trước model `z_model = z_source - z_ground - delta`; phép ngược `z_source = z_model + delta + z_ground`.
- Quyết định khi gặp lỗi batch: dừng và xác minh phép đổi tọa độ khi toàn bộ hộp cùng lệch z; không nhầm với A/B/C.
- Điều chưa chắc: QC là ca tạo có kiểm soát, không cho biết độ chính xác thực tế của model trên PCD.

## 8. Kết luận cuối

Qua ba lượt A/B/C, nhóm quan sát phản ứng của model khi chủ ý đổi delta hoặc pillar; khác biệt về số hộp/lớp là kết quả thí nghiệm, không phải bằng chứng lỗi pipeline. Trong ba ca QC, chỉ `case-batch-z` mô phỏng lỗi pipeline: 13/13 hộp cùng lệch z −1.805 m trong khi các trường còn lại giữ nguyên. `case-correct` lệch 0/13; `case-one-box-z` lệch 1/13. Khi gặp batch-z cần dừng và xác minh phép đổi z ngược; khi chỉ một hộp lệch thì kiểm tra hộp đó riêng. Các kết quả chỉ phục vụ thực hành, không phải ground truth và không được import vào CVAT.

## LC ghi nhận riêng

> LC ghi nhận ngày 01/10/2026. **Kết luận: ĐẠT.**

- **Quyền dùng PCD/image và đúng ca:** Gói Student KITTI 000008, không dùng dữ liệu Robotaxi. Thông tin chạy đã điền lại đầy đủ (image ID, checkpoint, input SHA-256, z_ground, code) và **khớp `smoke.json`**, kể cả giờ và thời gian từng bước.
- **Có chạy thật / chỉ phân tích; còn cần lượt thực hành bổ sung:** Chạy thật 2 lần, cả hai passed, cùng ra 1/13/6. Không cần chạy thêm.
- **Output đủ, giữ bản gốc, không đưa ca lỗi vào CVAT:** Đủ output (đã nộp ở lần 1). Báo cáo ghi rõ không import kết quả và `case-*.json` vào CVAT, không dùng làm ground truth.
- **Nhận xét từng thành viên và quyết định dừng pipeline:** **Đã sửa lỗi cốt lõi:** A/B/C là thí nghiệm nhóm chủ ý đổi delta/pillar, chỉ `case-batch-z` là lỗi pipeline. Phân biệt được dấu hiệu: lỗi batch thì số hộp và mọi trường khác giữ nguyên, chỉ z lệch đều. Bảng 3 ca lỗi đủ số (0/13, 13/13 −1,805 m, 1/13). Ghi đúng C có 6 `pedestrian`, 0 `vehicles`, nêu được checkpoint train với pillar 0,16. Mỗi người đủ 5 ý, gồm phép z thuận/ngược và điều chưa chắc.
- **Đồng ý chuyển sang chỉnh/QC / cần bổ sung; lý do:** **Đồng ý chuyển sang chỉnh/QC.** Cảm ơn nhóm đã sửa đến cùng.

