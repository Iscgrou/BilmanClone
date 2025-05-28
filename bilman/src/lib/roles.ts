export enum UserRole {
  Admin = 'admin',
  Operator = 'operator',
  Representative = 'representative',
}

export function hasRole(userRole: UserRole, requiredRole: UserRole): boolean {
  const roleHierarchy = [UserRole.Representative, UserRole.Operator, UserRole.Admin];
  return roleHierarchy.indexOf(userRole) >= roleHierarchy.indexOf(requiredRole);
}
