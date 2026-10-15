@echo off
TITLE Eclipse ioFog ECN Deployer (via WSL2)
cls
echo ============================================================
echo   🌐 ECLIPSE IOFOG EDGE COMPUTE NETWORK (ECN) DEPLOYER
echo ============================================================
echo.
echo Sanitizing Linux environment and deploying ioFog...
echo.

wsl -u root bash -c "echo 'vklak ALL=(ALL) NOPASSWD:ALL' > /etc/sudoers.d/vklak && chmod 0440 /etc/sudoers.d/vklak"
wsl bash -c "export PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin && mkdir -p ~/.local/bin && if [ ! -f ~/.local/bin/iofogctl ]; then echo 'Downloading iofogctl for Linux...'; curl -sL https://github.com/eclipse-iofog/iofogctl/releases/download/v3.9.0/iofogctl_3.9.0_amd64.tar.gz -o ~/iofogctl.tar.gz && tar -xzf ~/iofogctl.tar.gz -C ~/.local/bin/ iofogctl; fi && ~/.local/bin/iofogctl deploy -f /mnt/e/Cloud/smart-water-monitoring-iofog/iofog/controlplane.yaml && ~/.local/bin/iofogctl deploy -f /mnt/e/Cloud/smart-water-monitoring-iofog/iofog/ecn.yaml"

echo.
echo ============================================================
echo Execution complete! Check status with: wsl bash -c "export PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin && ~/.local/bin/iofogctl get all"
echo ============================================================
pause
