export const formatFileSize = (bytes) => {
  if (!bytes) return '0 B'
  
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(1024))
  return `${(bytes / Math.pow(1024, i)).toFixed(1)} ${sizes[i]}`
}

export const formatDate = (date) => {
  if (!date) return '-'
  
  const d = new Date(date)
  const now = new Date()
  const diffTime = Math.abs(now - d)
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
  
  if (diffDays === 1) return 'Yesterday'
  if (diffDays < 7) return `${diffDays} days ago`
  if (diffDays < 30) return `${Math.floor(diffDays / 7)} weeks ago`
  if (diffDays < 365) return `${Math.floor(diffDays / 30)} months ago`
  
  return d.toLocaleDateString()
}

export const formatNumber = (num) => {
  if (!num) return '0'
  return new Intl.NumberFormat().format(num)
}

export const formatPercentage = (value, total) => {
  if (!total) return '0%'
  return `${((value / total) * 100).toFixed(1)}%`
}

export const truncateText = (text, maxLength = 50) => {
  if (!text) return ''
  return text.length > maxLength ? `${text.substring(0, maxLength)}...` : text
}

export const extractDomain = (email) => {
  if (!email || !email.includes('@')) return email
  return email.split('@')[1]
}

export const formatDuration = (seconds) => {
  if (!seconds) return '0s'
  
  if (seconds < 60) return `${seconds.toFixed(1)}s`
  if (seconds < 3600) return `${Math.floor(seconds / 60)}m ${Math.floor(seconds % 60)}s`
  
  const hours = Math.floor(seconds / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)
  return `${hours}h ${minutes}m`
}