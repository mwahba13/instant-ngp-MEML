#pragma once

#include <chrono>

class NGPSequencer
{
public:

	void StartTimer();
	void IncrementTimer();


	bool isTimerRunning = true;
	//timer that starts at the beginning of a loaded sequence in seconds.
	float m_timer;

private:
	std::chrono::steady_clock::time_point m_startTime;
	std::chrono::steady_clock::time_point m_currentTime;
};
