import { type BaseResponse } from '@/models/base'

// 获取内置插件分类接口响应接口

export type GetCategoriesResponse = BaseResponse<
  Array<{
    category: string
    icon: string
    name: string
  }>
>

export type GetBuiltinToolsResponse = BaseResponse<
  Array<{
    background: string
    category: string
    name: string
    created_at: number
    description: string
    label: string
    tools: Array<any>
  }>
>
