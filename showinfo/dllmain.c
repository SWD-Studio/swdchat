/* Replace "dll.h" with the name of your header */
#include "dll.h"
#include <windows.h>

DLLIMPORT void info() {
	NOTIFYICONDATA nid = {sizeof(nid)};
	nid.uFlags = NIF_INFO;
	nid.dwInfoFlags = NIIF_INFO;
	strcpy_s(nid.szInfoTitle, sizeof(nid.szInfoTitle), "SWDChat");
	strcpy_s(nid.szInfo, sizeof(nid.szInfo), "����Ϣ");
	Shell_NotifyIcon(NIM_ADD, &nid);
	Sleep(2 * 1000);
	Shell_NotifyIcon(NIM_DELETE, &nid);
	//MessageBox(0,"Hello World from DLL!\n","Hi",MB_ICONINFORMATION);
}

BOOL WINAPI DllMain(HINSTANCE hinstDLL, DWORD fdwReason, LPVOID lpvReserved) {
	switch (fdwReason) {
		case DLL_PROCESS_ATTACH: {
			break;
		}
		case DLL_PROCESS_DETACH: {
			break;
		}
		case DLL_THREAD_ATTACH: {
			break;
		}
		case DLL_THREAD_DETACH: {
			break;
		}
	}

	/* Return TRUE on success, FALSE on failure */
	return TRUE;
}
