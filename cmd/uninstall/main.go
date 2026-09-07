package main

import (
	"os"
	"os/exec"
	"syscall"
	"unsafe"
)

var (
	moduser32 = syscall.NewLazyDLL("user32.dll")
	procMsgBox = moduser32.NewProc("MessageBoxW")
)

const (
	MB_YESNO      = 0x00000004
	MB_ICONQUESTION = 0x00000020
	MB_ICONINFO   = 0x00000040
	IDYES         = 6
)

func messageBox(title, text string, style uint) int {
	tPtr, _ := syscall.UTF16PtrFromString(title)
	mPtr, _ := syscall.UTF16PtrFromString(text)
	r, _, _ := procMsgBox.Call(0, uintptr(unsafe.Pointer(mPtr)), uintptr(unsafe.Pointer(tPtr)), uintptr(style))
	return int(r)
}

func main() {
	res := messageBox(
		"Uninstall Tally Connect",
		"Are you sure you want to stop all background services and uninstall Tally Connect?",
		MB_YESNO|MB_ICONQUESTION,
	)
	if res != IDYES {
		os.Exit(0)
	}

	// Terminate any running TallyConnect.exe
	_ = exec.Command("taskkill", "/F", "/IM", "TallyConnect.exe", "/T").Run()

	// Remove registry startup key via reg command (built-in Windows utility)
	_ = exec.Command("reg", "delete", `HKCU\Software\Microsoft\Windows\CurrentVersion\Run`, "/v", "TallyConnectTray", "/f").Run()

	messageBox(
		"Tally Connect Uninstalled",
		"Tally Connect services stopped and Windows Startup entries removed successfully.",
		MB_ICONINFO,
	)
}
