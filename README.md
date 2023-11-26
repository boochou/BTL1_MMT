# BTL1_MMT

Yêu cầu: máy tính cần có python 3 để chạy. Riêng với máy làm server cần tải thêm mySQL và tạo bảng theo câu lệnh sau: 
CREATE TABLE account (
    username VARCHAR(50),
    pass VARCHAR(64),
    _port INT,
    ipaddr VARCHAR(255),
    fname VARCHAR(255),
    fpath VARCHAR(255),
    PRIMARY KEY (username, fname)
);

Hướng dẫn sử dụng:
Trước hết, vui lòng tạo repo_recieve sẵn trong thư mục
1. Đối với phiên bản terminal:
- Với server: python runServer.py
- Với client: python runClient.py
2. Đối với phiên bản GUI:
- Với server: python GUI_runServer.py
- Với client: python GUI_runClient.py

 
