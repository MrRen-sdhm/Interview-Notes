#pragma once
#ifndef DEBUGCLASS_H
#define DEBUGCLASS_H
#include <stdlib.h>
#include <windows.h>
#include <iostream>

class DebugInfo
{
	DebugInfo() { std::cout << "constructor DebugInfo, this: \n" << this; }
	~DebugInfo() { std::cout << "destructor DebugInfo, this: \n" << this; }

public:
	static void PrintIntArry(const int* intput, size_t size, const char* info);

};

void DebugInfo::PrintIntArry(const int* input, size_t size, const char* info)
{
    int i = 0;
    std::cout << info << std::endl;
    while (size--)
    {
        std::cout << " " << input[i++];
    }
    std::cout << "\n" << std::endl;
}
#endif // !DEBUGCLASS_H