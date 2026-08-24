export const apiPrefix: string = 'http://127.0.0.1:5000'

//业务状态码
export const httpCode = {
  success: 'success',
  fail: 'fail',
  notFound: 'notFound',
  unauthorized: 'unauthorized',
  forbidden: 'forbidden',
  validateError: 'validate_error',
}

//类型字符串与中文映射
export const typeMap: Record<string, string> = {
  str: '字符串',
  int: '整型',
  float: '浮点型',
  bool: '布尔型',
}
