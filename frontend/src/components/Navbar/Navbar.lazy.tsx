import React, { lazy, Suspense } from 'react';

const LazyNavbar = lazy(() => import('./Navbar'));

const Navbar = (props: JSX.IntrinsicAttributes & { children?: React.ReactNode; }) => (
  <Suspense fallback={null}>
    <LazyNavbar {...props} />
  </Suspense>
);

export default Navbar;
