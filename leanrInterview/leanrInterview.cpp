// leanrInterview.cpp : 此文件包含 "main" 函数。程序执行将在此处开始并结束。
//
#include <stdlib.h>
#include <windows.h>
#include <iostream>
#include <map>

#include "database.h"
#include "DebugClass.h"

/*
*   传入一个数组，打印重复出现的num
*   exp， input {1， 2， 1， 3， 2}
*         print 1，2
*/
bool FindRepeterNumByMap(int* input, size_t size)
{
    DebugInfo::PrintIntArry(input, size, "got input nums: ");
    std::map<int, int> Mapp;

    for (int i = 0; i < size; i++)
    {
        if (Mapp[input[i]] != input[i]) {
            Mapp[input[i]] = input[i];
        } else {
            std::cout << "Repater num: " << input[i] << std::endl;
        }
    }
    return true;
}

/*
*   传入一个数组，打印重复出现的num
*   exp， input {1， 2， 1， 3， 2}
*         print 1，2
*/
bool FindRepeterNumByTemp(int* input, size_t size)
{
    DebugInfo::PrintIntArry(input, size, "got input nums: ");

    int temp;
    for (int i = 0; i < size; ++i)
    {
        while (input[i] != i) {
            temp = input[i];
            if (input[i] == input[temp]) {
                std::cout << "Repater num: " << input[i] << ", i: " << i << std::endl;
                break;
            }
            input[i] = input[temp];
            input[temp] = temp;
        }
    }
    return true;
}
int main()
{
    std::cout << "Hello World!\n";
    //FindRepeterNumByMap(RamRepeatArray, 20);
    FindRepeterNumByTemp(RamRepeatArray, 20);
    return 0;
}


