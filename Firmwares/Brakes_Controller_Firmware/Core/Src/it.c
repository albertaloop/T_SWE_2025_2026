/*
 * it.c
 *
 *      Albertalooop CANbus normal 2 node test
 *      Created on: 06-25-2025
 *      Author: Jaspreet Chhabra
 *      Ref: kiran
 */

#include "main_app.h"

extern CAN_HandleTypeDef hcan1;
extern TIM_HandleTypeDef htimer6;
extern void CAN1_Tx(uint8_t remote);

/**
  * @brief System Clock Configuration
  * @retval None
  */
void SysTick_Handler (void)
{
	HAL_IncTick();
	HAL_SYSTICK_IRQHandler();
}

/**
  * @brief This function handles CAN_TX interrupts.
  */
void CAN1_TX_IRQHandler(void)
{
	HAL_CAN_IRQHandler(&hcan1);
}

/**
  * @brief This function handles CAN_RX0 interrupts.
  */
void CAN1_RX0_IRQHandler(void)
{
	HAL_CAN_IRQHandler(&hcan1);
}

/**
  * @brief This function handles CAN SCE interrupt.
  */
void CAN1_SCE_IRQHandler(void)
{
	HAL_CAN_IRQHandler(&hcan1);
}

/**
  * @brief This function handles Timer 6 interrupt and DAC underrun interrupts.
  */
void TIM6_DAC_IRQHandler(void)
{
	HAL_TIM_IRQHandler(&htimer6);
}

/**
  * @brief This function handles EXTI line[15:10] interrupts.
  * Waits for button to be pressed then sends the CAN bus message
  */
void EXTI15_10_IRQHandler(void)
{
	HAL_TIM_Base_Start_IT(&htimer6);
	HAL_GPIO_EXTI_IRQHandler(GPIO_PIN_13);
}


