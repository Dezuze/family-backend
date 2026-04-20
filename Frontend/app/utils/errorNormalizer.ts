export function friendlyErrorMessage(error: any, status?: number) {
  // If server provided a user-friendly message, prefer it
  if (error && typeof error === 'object') {
    if (error.error) return String(error.error)
    if (error.detail) return String(error.detail)
  }

  // Map common HTTP status codes to friendly messages
  if (status === 403) return "You don't have permission to make changes — contact the technical team for help."
  if (status === 404) return "The requested item was not found."
  if (status === 400) return "There was a problem with the entered data. Please check and try again."
  // Fallback
  return "An unexpected error occurred. Please contact the technical team for help."
}

export default friendlyErrorMessage
