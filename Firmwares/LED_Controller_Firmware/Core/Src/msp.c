/*
 * msp.c
 *
 *      Albertalooop CANbus normal 2 node test
 *      Created on: 06-25-2025
 *      Author: Jaspreet Chhabra
 *      Ref: kiran
 */


#include "main_app.h"

/**
  * @brief  Initialize the MSP.
  * @retval None
  */
void HAL_MspInit(void)
{
  //Here will do low level processor specific inits.
  //1. Set up the priority grouping of the arm cortex mx processor
  HAL_NVIC_SetPriorityGrouping(NVIC_PRIORITYGROUP_4);

  //2. Enable the required system exceptions of the arm cortex mx processor
  SCB->SHCSR |= 0x7 << 16; //usage fault, memory fault and bus fault system exceptions

  //3. configure the priority for the system exceptions
  HAL_NVIC_SetPriority(MemoryManagement_IRQn,0,0);
  HAL_NVIC_SetPriority(BusFault_IRQn,0,0);
  HAL_NVIC_SetPriority(UsageFault_IRQn,0,0);
}

/**
  * @brief  UART MSP Init.
  * @param  huart  Pointer to a UART_HandleTypeDef structure that contains
  *                the configuration information for the specified UART module.
  * @retval None
  */
void HAL_UART_MspInit(UART_HandleTypeDef *huart)
{
  GPIO_InitTypeDef gpio_uart;
  //here we are going to do the low level inits. of the USART2 peripheral

  //1. enable the clock for the USART2 peripheral as well as for GPIOA peripheral
  __HAL_RCC_USART2_CLK_ENABLE();
  __HAL_RCC_GPIOA_CLK_ENABLE();

  //2 . Do the pin muxing configurations
  gpio_uart.Pin = GPIO_PIN_2;
  gpio_uart.Mode =GPIO_MODE_AF_PP;
  gpio_uart.Pull = GPIO_PULLUP;
  gpio_uart.Speed = GPIO_SPEED_FREQ_LOW;
  gpio_uart.Alternate =  GPIO_AF7_USART2; //UART2_TX
  HAL_GPIO_Init(GPIOA,&gpio_uart);

  gpio_uart.Pin = GPIO_PIN_3; //UART2_RX
  HAL_GPIO_Init(GPIOA,&gpio_uart);
  //3 . Enable the IRQ and set up the priority (NVIC settings )
  HAL_NVIC_EnableIRQ(USART2_IRQn);
  HAL_NVIC_SetPriority(USART2_IRQn,15,0);
}

/**
  * @brief  Initializes the CAN MSP.
  * @param  hcan pointer to a CAN_HandleTypeDef structure that contains
  *         the configuration information for the specified CAN.
  * @retval None
  */
void HAL_CAN_MspInit(CAN_HandleTypeDef *hcan)
{
  GPIO_InitTypeDef GPIO_InitStruct;

  __HAL_RCC_CAN1_CLK_ENABLE();

  /**CAN1 GPIO Configuration
     PA11     ------> CAN1_RX
     PA12     ------> CAN1_TX
  */
  GPIO_InitStruct.Pin = GPIO_PIN_11|GPIO_PIN_12;
  GPIO_InitStruct.Mode = GPIO_MODE_AF_PP;
  GPIO_InitStruct.Pull = GPIO_NOPULL;
  GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_VERY_HIGH;
  GPIO_InitStruct.Alternate = GPIO_AF9_CAN1;
  HAL_GPIO_Init(GPIOA, &GPIO_InitStruct);

  HAL_NVIC_SetPriority(CAN1_TX_IRQn,15,0);
  HAL_NVIC_SetPriority(CAN1_RX0_IRQn,15,0);
  HAL_NVIC_SetPriority(CAN1_RX1_IRQn,15,0);
  HAL_NVIC_SetPriority(CAN1_SCE_IRQn,15,0);

  HAL_NVIC_EnableIRQ(CAN1_TX_IRQn);
  HAL_NVIC_EnableIRQ(CAN1_RX0_IRQn);
  HAL_NVIC_EnableIRQ(CAN1_RX1_IRQn);
  HAL_NVIC_EnableIRQ(CAN1_SCE_IRQn);
}

/**
  * @brief  Initializes the TIM Base MSP.
  * @param  htim TIM Base handle
  * @retval None
  */
void HAL_TIM_Base_MspInit(TIM_HandleTypeDef *htimer)
{
  //1. enable the clock for the TIM6 peripheral
  __HAL_RCC_TIM6_CLK_ENABLE();

  //2. Enable the IRQ of TIM6
  HAL_NVIC_EnableIRQ(TIM6_DAC_IRQn);

  //3. setup the priority for TIM6_DAC_IRQn
  HAL_NVIC_SetPriority(TIM6_DAC_IRQn,15,0);
}



