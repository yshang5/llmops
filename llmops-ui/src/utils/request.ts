import { apiPrefix, httpCode } from '@/config'
import { Message } from '@arco-design/web-vue'

const TIME_OUT = 100000

const baseFetchOptions = {
  method: 'GET',
  mode: 'cors',
  credentials: 'include',
  headers: {
    'Content-Type': 'application/json',
  },
  redirect: 'follow',
}

type FetchOptionType = Omit<RequestInit, 'body'> & {
  params?: Record<string, string>
  body?: BodyInit | Record<string, unknown> | null
}

const baseFetch = <T>(url: string, fetchOption: FetchOptionType): Promise<T> => {
  const options: typeof baseFetchOptions & FetchOptionType = Object.assign(
    {},
    baseFetchOptions,
    fetchOption,
  )

  let urlWithPrefix = `${apiPrefix}${url.startsWith('/') ? url : `/${url}`}`
  if (url.search(/\?/) == -1) {
    urlWithPrefix += '?'
  } else {
    urlWithPrefix += '&'
  }
  const { method, params, body } = options

  //如果请求是get方法，且有param方法
  if (method === 'GET' && params) {
    Object.keys(params).forEach((key) => {
      const value = params[key]
      if (value) {
        urlWithPrefix += `${key}=${encodeURIComponent(value)}&`
      }
    })
  }

  delete options.params

  if (body) {
    options.body = JSON.stringify(body)
  }

  let timeoutId: ReturnType<typeof setTimeout>
  const timeoutPromise = new Promise((_, reject) => {
    timeoutId = setTimeout(() => {
      reject(new Error('接口已经超时'))
    }, TIME_OUT)
  })

  const fetchPromise = new Promise((resolve, reject) => {
    globalThis
      .fetch(urlWithPrefix, options as RequestInit)
      .then(async (res) => {
        const json = await res.json()
        if (json.code === httpCode.success) {
          resolve(json)
        } else {
          Message.error(json.message)
          reject(new Error(json.message))
        }
      })
      .catch((err) => {
        Message.error(err)
        reject(err)
      })
  })

  return Promise.race([timeoutPromise, fetchPromise]).finally(() => {
    clearTimeout(timeoutId)
  }) as Promise<T>
}

export const request = <T>(url: string, options = {}) => {
  return baseFetch<T>(url, options)
}

export const get = <T>(url: string, options = {}) => {
  return baseFetch<T>(url, Object.assign({}, options, { method: 'GET' }))
}

export const post = <T>(url: string, options = {}) => {
  return baseFetch<T>(url, Object.assign({}, options, { method: 'POST' }))
}
