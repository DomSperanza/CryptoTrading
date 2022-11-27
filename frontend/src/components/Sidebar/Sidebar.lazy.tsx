import React, { lazy, Suspense } from 'react';

const LazySidebar = lazy(() => import('./Sidebar'));

const Sidebar = (props: JSX.IntrinsicAttributes & { children?: React.ReactNode; }) => (
  <Suspense fallback={null}>
    <LazySidebar> Loading... </LazySidebar>
  </Suspense>
);

export default Sidebar;
