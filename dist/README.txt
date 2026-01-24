LinkerHand HTTP API 服务 - 部署包
========================================

文件说明:
  - linkerhand_service.exe: 主程序
  - deploy.bat: 一键部署脚本（右键以管理员身份运行）
  - start_service.bat: 启动服务
  - stop_service.bat: 停止服务
  - restart_service.bat: 重启服务
  - uninstall_service.bat: 卸载服务（删除开机自启动）

快速部署:
  1. 右键点击 deploy.bat
  2. 选择"以管理员身份运行"
  3. 按照提示完成安装

服务管理:
  启动: start_service.bat
  停止: stop_service.bat
  重启: restart_service.bat
  卸载: uninstall_service.bat

验证安装:
  重启电脑后，访问 http://localhost:8000

日志说明:
  - 日志文件保存在 logs/ 目录下
  - 日志文件按日期命名: linkerhand_service_YYYYMMDD.log
  - 每个日志文件最大10MB，保留5个备份
  - 服务在后台运行，不会弹出窗口
