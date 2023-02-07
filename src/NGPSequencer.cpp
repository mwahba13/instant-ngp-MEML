#include "neural-graphics-primitives/NGPSequencer.h"


void NGPSequencer::StartTimer()
{
	isTimerRunning = true;
	m_startTime = std::chrono::steady_clock::now();
	printf("\n---------Start timer--------------");
}

void NGPSequencer::IncrementTimer()
{
	printf("----------run timer: %f \n",&m_timer);
	m_currentTime = std::chrono::steady_clock::now();

	m_timer = std::chrono::duration_cast<std::chrono::seconds>(m_currentTime - m_startTime).count();

}
