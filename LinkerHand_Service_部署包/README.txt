LinkerHand HTTP API 服务 - 部署包
========================================

文件说明:
  - linkerhand_service.exe: 主程序
  - uninstall_service.bat: 卸载脚本
  - start_service.bat: 启动服务
  - stop_service.bat: 停止服务
  - restart_service.bat: 重启服务
  - check_service_status.bat: 检查服务状态

快速安装:
  1. 右键点击 deploy_to_other_pc.bat
  2. 选择"以管理员身份运行"
  3. 按照提示完成安装

验证安装:
  重启电脑后，访问 http://localhost:8000

服务管理:
  启动: start_service.bat
  停止: stop_service.bat
  重启: restart_service.bat
  状态: check_service_status.bat
  卸载: uninstall_service.bat
